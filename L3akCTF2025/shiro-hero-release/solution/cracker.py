#!/usr/bin/env python3
from typing import List, Optional, Tuple, Any
from z3 import BitVec, RotateLeft, Solver, sat, BitVecRef
M64 = (1 << 64) - 1


def _rotl64(x: int, k: int) -> int:
    """
    Left-rotate a 64-bit integer x by k bits, mod 2^64.
    """
    return ((x << k) | (x >> (64 - k))) & M64


class Xoshiro256:
    """
    Pure-Python implementation of Xoshiro256** (aka Xoshiro256 estrellas estrellas).
    - Internal state: 4 * 64-bit words (list[int] of length 4).
    - 'step' function returns the untempered result (just s[1]).
    - '__call__' applies the temper function to 'step' and returns the final output.
    """

    inv9: int = pow(9, -1, 1 << 64)   # modular inverse of 9 mod 2^64
    inv5: int = pow(5, -1, 1 << 64)   # modular inverse of 5 mod 2^64

    def __init__(self, seed: List[int]):
        """
        Initialize Xoshiro256 with a 4-element list of 64-bit integers.
        """
        if len(seed) != 4:
            raise ValueError("Seed must be a list of 4 integers (each < 2^64).")

        # Ensure each element is masked to 64 bits
        self._state = [s & M64 for s in seed]

    @staticmethod
    def temper(s1: int) -> int:
        """
        Temper function: rotl64((s1 * 5) & M64, 7) * 9 & M64
        """
        return (_rotl64((s1 * 5) & M64, 7) * 9) & M64

    @staticmethod
    def untemper(y: int) -> int:
        """
        Inverse of `temper`: undo rotl + multiplication by 9 mod 2^64.
        Provided for completeness, but not used in the predictor itself.
        """
        # First un-multiply by 9 mod 2^64, then un-rotate left by 7, then un-multiply by 5.
        # Equivalent to: x = (rotl64((y * inv9) & M64, 64 - 7) * inv5) & M64
        return (_rotl64((y * Xoshiro256.inv9) & M64, 64 - 7) * Xoshiro256.inv5) & M64

    def step(self) -> int:
        """
        Perform one iteration of the 'step' function. Returns the untempered output, which is s[1].
        Updates the internal state in-place.
        """
        s0, s1, s2, s3 = self._state

        result = s1
        t = (s1 << 17) & M64

        s2 ^= s0
        s3 ^= s1
        s1 ^= s2
        s0 ^= s3
        s2 ^= t
        s3 = _rotl64(s3, 45)

        self._state = [s0 & M64, s1 & M64, s2 & M64, s3 & M64]
        return result

    def __call__(self) -> int:
        """
        Return the tempered 64-bit output: temper(step()).
        """
        untempered = self.step()
        return Xoshiro256.temper(untempered)



class Xoshiro256Predictor:
    """
    Given a list of consecutive, untempered Xoshiro256 outputs, recover the 4×64-bit seed
    via Z3, then allow prediction of any subsequent tempered outputs.
    """

    def __init__(self, observed_untempered: List[int]):
        """
        observed_untempered: a list of consecutive 64-bit outputs from Xoshiro256.step(),
                             BEFORE tempering. Length must be >= 4 to get a unique solution.
        """
        if len(observed_untempered) < 4:
            raise ValueError("At least 4 consecutive untempered outputs are required for seed recovery.")
        for v in observed_untempered:
            if not (0 <= v < (1 << 64)):
                raise ValueError(f"Each observed output must be a 64-bit integer. Invalid value: {v}")

        # Keep a copy of the observed untempered outputs
        self._observed = observed_untempered[:]

        # Placeholders for once the seed is recovered:
        self._seed: Optional[List[int]] = None
        self._engine: Optional[Xoshiro256] = None

    @staticmethod
    def _z3_step(state_vars: List[BitVecRef]) -> Tuple[BitVecRef, List[BitVecRef]]:
        """
        Build Z3 constraints for one Xoshiro256 'step' (untempered).
        Input:
            state_vars: a list of 4 Z3 BitVecs, each 64 bits, representing [s0, s1, s2, s3].
        Returns:
            (output_var, next_state_vars)
            - output_var is the BitVec corresponding to the untempered result (previous s1).
            - next_state_vars is a list of 4 BitVecs representing the updated state after the step.
        """
        s0, s1, s2, s3 = state_vars

        # In the algorithm, result = s1
        result = s1

        # t = (s1 << 17) & M64
        t = (s1 << 17) & M64

        # The in-place XOR updates (we must create new BitVecs for each):
        s2_new = s2 ^ s0
        s3_new = s3 ^ s1
        s1_new = s1 ^ s2_new
        s0_new = s0 ^ s3_new
        s2_new = s2_new ^ t
        s3_new = RotateLeft(s3_new, 45)

        # Mask every new state to 64 bits (since all BitVecs are 64 bits, they auto-wrap around).
        # Build the list in the same [s0, s1, s2, s3] order:
        next_state = [s0_new, s1_new, s2_new, s3_new]
        return result, next_state

    def recover_seed(self) -> List[int]:
        """
        Recover the unknown 4×64-bit seed by solving Z3 constraints.
        After calling this, `self._seed` is set to [s0, s1, s2, s3].
        Returns:
            The recovered seed as a list of four 64-bit Python ints.
        Raises:
            RuntimeError if Z3 finds unsatisfiable or cannot solve.
        """
        if self._seed is not None:
            # Seed already recovered; return immediately.
            return self._seed

        # Step A: Create four fresh 64-bit BitVecs:
        s_vars = [BitVec(f"s{i}", 64) for i in range(4)]

        solver = Solver()

        # We'll keep a copy of state_vars, updating it each iteration:
        state_vars = s_vars[:]

        # For each observed untempered output, add constraints that Z3_step() == observed[i].
        for i, obs in enumerate(self._observed):
            out_i, next_state = Xoshiro256Predictor._z3_step(state_vars)
            solver.add(out_i == obs)
            state_vars = next_state  # feed the next state into the next iteration

        # Ask Z3 to solve:
        if solver.check() != sat:
            raise RuntimeError("Z3 could not find a satisfying assignment for the given observed outputs.")

        model = solver.model()
        recovered = []
        for i in range(4):
            val = model.evaluate(s_vars[i])
            recovered.append(val.as_long() & M64)  # type: ignore

        # Save the seed internally
        self._seed = recovered

        # Initialize the local engine with this seed, but consume as many steps as we already used:
        # We need to “fast-forward” our pure-Python engine through exactly len(self._observed) steps,
        # because each observed output corresponded to one untempered step.
        engine = Xoshiro256(self._seed)
        for _ in range(len(self._observed)):
            engine.step()  # discard, just to synchronize

        self._engine = engine
        return self._seed

    def predict(self, count: int) -> List[int]:
        """
        Predict the next `count` tempered outputs of Xoshiro256**.
        Precondition: `recover_seed()` must have been called (so that self._engine is not None).
        Returns:
            A list of `count` future 64-bit outputs.
        Raises:
            RuntimeError if `.recover_seed()` was not called before.
        """
        if self._engine is None:
            raise RuntimeError("Seed not recovered yet. Call `recover_seed()` first.")

        predictions = []
        for _ in range(count):
            predictions.append(self._engine())
        return predictions

    def get_state(self) -> Optional[List[int]]:
        """
        Return the recovered seed (if available), else None.
        """
        return self._seed

    def reset(self) -> None:
        """
        Clear any recovered seed and engine, allowing a fresh recovery attempt.
        """
        self._seed = None
        self._engine = None


'''
if __name__ == "__main__":
    import random as rnd
    random  = rnd.SystemRandom()

    # 1) Generate a random seed
    true_seed = [random.getrandbits(64) for _ in range(4)]
    real_engine = Xoshiro256(true_seed)

    # 2) Produce N consecutive untempered outputs
    N = 44
    observed = [real_engine.step() for _ in range(N)]

    # 3) Attempt to recover
    predictor = Xoshiro256Predictor(observed_untempered=observed)
    recovered_seed = predictor.recover_seed()

    print("True seed:     ", [hex(x) for x in true_seed])
    print("Recovered seed:", [hex(x) for x in recovered_seed])

    # 4) Now ask for the next few tempered outputs
    next_temps_true = [real_engine() for _ in range(5)]
    next_temps_pred = predictor.predict(5)
    print("True next 5 tempered:", [hex(x) for x in next_temps_true])
    print("Pred next 5 tempered:", [hex(x) for x in next_temps_pred])
    assert next_temps_true == next_temps_pred, "Prediction did not match actual!"
'''
