#!/usr/localbin/sage
from sage.all import *
import time
from hashlib import sha3_256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


USE_FLATTER = True
DEBUG_ROOTS = None
Bound_Check = False


Ciphertext = '41b53384d92de5c678a2138a0da552d174d77c420591b29ccb7c7610310bf82bcb58f903a423d7d257e3ee4ae2c4da69'
p   = 2814112013697373133393152975842584191818662382013600787892419349345515176682276313810715094745633257074198789308535071537342445016418881801789390548709414391857257571565758706478418356747070674633497188053050875416821624325680555826071110691946607460873056965360830571590242774934226866183966309185433462514537484258655982386235046029227507801410907163348439547781093397260096909677091843944555754221115477343760206979650067087884993478012977277878532807432236554020931571802310429923167588432457036104110850960439769038450365514022349625383665751207169661697352732236111926846454751701734527011379148175107820821297628946795631098960767492250494834254073334414121627833939461539212528932010726136689293688815665491671395174710452663709175753603774156855766515313827613727281696692633529666363787286539769941609107777183593336002680124517633451490439598324823836457251219406391432635639225604556042396004307799361927379900586400420763092320813392262492942076312933268033818471555255820639308889948665570202403815856313578949779767046261845327956725767289205262311752014786247813331834015084475386760526612217340579721237414485803725355463022009536301008145867524704604618862039093555206195328240951895107040793284825095462530151872823997171764140663315804309008611942578380931064748991594407476328437785848825423921170614938294029483257162979299388940695877375448948081108345293394327808452729789834135140193912419661799488795210328238112742218700634541149743657287232843426369348804878993471962403393967857676150371600196650252168250117793178488012000505422821362550520509209724459895852366827477851619190503254853115029403132178989005195751194301340277282730390683651120587895060198753121882187788657024007291784186518589977788510306743945896108645258766415692825664174470616153305144852273884549635059255410606458427323864109506687636314447514269094932953219924212594695157655009158521173420923275882063327625408617963032962033572563553604056097832111547535908988433816919747615817161606620557307000377194730013431815560750159027842164901422544571224546936793234970894954668425436412347785376194310030139080568383420772628618722646109707506566928102800033961704343991962002059794565527774913883237756792720065543768640792177441559278272350823092843683534396679150229676101834243787820420087274028617212684576388733605769491224109866592577360666241467280158988605523486345880882227855505706309276349415034547677180618296352866263005509222254318459768194126727603047460344175581029298320171226355234439676816309919127574206334807719021875413891580871529049187829308412133400910419756313021540478436604178446757738998632083586207992234085162634375406771169707323213988284943779122171985953605897902291781768286548287878180415060635460047164104095483777201737468873324068550430695826210304316336385311384093490021332372463463373977427405896673827544203128574874581960335232005637229319592369288171375276702260450911735069504025016667755214932073643654199488477010363909372005757899989580775775126621113057905717449417222016070530243916116705990451304256206318289297738303095152430549772239514964821601838628861446301936017710546777503109263030994747397618576207373447725441427135362428360863669327157635983045447971816718801639869547525146305655571843717916875669140320724978568586718527586602439602335283513944980064327030278104224144971883680541689784796267391476087696392191
h   = 1420555256339029007623997813064646001269162517128321148445315195505239735275630861823661566974806499472047280215484592996005803648513302169629626127099758282515738821101977445273485022910246569722391022977450955342222836145985252124058212342529128780170990021228730988558665064173954220322773988555167710669068750665776903981634200337373777404012466927646596680586333670581651645526694895600877689342038116459849183193823872501035663586605107067192354044210531807251755452156351983674662886645745394856941265207731156473167231778757731819787611903442134906892597442296936233823840108134806009542341564017395586357285132443867104900170964829691269535011088959513758953200725927512241315102588162307625667497293774446856607793870742116890747893541277522373302165118962976053575406705355764971195021874784514615007411950628751457901414286417358960010967221053822454908696424925405704175995633020493142678213202614937742894400381343076316089897622795515556015286002072322759700438579099970591676839009309031769399502594275266218377682472239872586976705452556133518395328415914503518652542017532651647731241407171312901187911076641932472943264583606924316675349565466488903831076073348850535782518384829652304040155890590587188783695482711889391210316569992875826864203896074373913044155630807488027391070097591354568591831261212998547450723243648908349081702648981754965087366716012704456844050856945098481648381066456654298504766274287677173531407712216638604928122194203916328841926799970191645315242073698356237463109990735562385573707846536974481579821301372474435457099406760484280999724263427442692583436069170036373949813257024671755403669821456270665060921956691382969799591246457852441573272563366612307625286201260042625086965961053006988659415151285688613563697564208949796608132657497688137512977726996868089866737746050625960033949688003905344289968553237468369562275970721124808922797498954729192402174080310105048553480796371124861551154608423542660872024811406457451424253705687979915395138199662324871095873255085721494088182389344068642956910343125988440788281536821574417589504214561018112652377091738873567384795002650440795826732903483284697533314215503203322729252515102929675782158033940939707173384735831945973131378767145549237414530035857282428664740004024186722896592693839808003379490048051781800528316131147063192114353380299163535474170148552078839155797722939143164848128170591789817861428901096912042379655572487529983245927123870716371357517142431645561532273325783362132723664729122853387243023889022825534772304668999948890306453633124290070865560117725343418936602004343258378292218254184989796563841886060342528155126255491479519793234521554762270234424568183556174229507271089194135988143493032829906811846783521409480751862383365285419925324896562580231684692411694312251240562954259361596977465804532938260753882101880890334741978448410119591665004422790211098229717537610959221523324756588024738544068846236205437760843840319798491939909330547143199854608585823646613660809454152858803614876632067827324289956927912056108902075641611668181460557770913959037715741018607941206784764550084749008826004455090269295539665469266276760215529247213893160911919455625283080509926624966775395334197154212462026901783136821516237970556846369147663455890608535960863730071819706481755582989771193307683239283077479511187437689338027648438450206074052
xi1 = 0.31
xi2 = 0.69
w   = 10


def matrix_overview(BB, bound):
    dims = BB.dimensions()
    print(f"[+] Matrix dimensions: {dims[0]} x {dims[1]}")
    print(f"Matrix Structure: (X=non-zero, O=zero)")
    for ii in range(BB.dimensions()[0]):
        a = ('%02d ' % ii)
        for jj in range(BB.dimensions()[1]):
            # if not zero, print the value
            a += '0' if BB[ii, jj] == 0 else 'X' # print value 
            a += ' '
        if BB[ii, jj] >= bound:
            a += '~'
        print(a)
        
def truncate_int(x: int, head: int = 20, tail: int = 20) -> str:
    """
    Return a string like  '1234567890...0987654321 (len=1000)'.
    """
    s = str(x)
    if len(s) <= head + tail + 3:
        return s
    return f"{s[:head]}…{s[-tail:]} (len={len(s)})"


def create_lattice(pr, shifts, bounds, order="invlex", sort_shifts_reverse=False, sort_monomials_reverse=False):
    """
    Creates a lattice from a list of shift polynomials.
    :param pr: the polynomial ring
    :param shifts: the shifts
    :param bounds: the bounds
    :param order: the order to sort the shifts/monomials by
    :param sort_shifts_reverse: set to true to sort the shifts in reverse order
    :param sort_monomials_reverse: set to true to sort the monomials in reverse order
    :return: a tuple of lattice and list of monomials
    """
    if pr.ngens() > 1:
        pr_ = pr.change_ring(ZZ, order=order)
        shifts = [pr_(shift) for shift in shifts]

    monomials = set()
    for shift in shifts:
        monomials.update(shift.monomials())

    shifts.sort(reverse=sort_shifts_reverse)
    monomials = sorted(monomials, reverse=sort_monomials_reverse)
    L = matrix(ZZ, len(shifts), len(monomials))
    for row, shift in enumerate(shifts):
        for col, monomial in enumerate(monomials):
            L[row, col] = shift.monomial_coefficient(monomial) * monomial(*bounds)

    monomials = [pr(monomial) for monomial in monomials]
    return L, monomials


def reduce_lattice(L, delta=0.8):
    """
    Reduces a lattice basis using a lattice reduction algorithm (currently LLL).
    :param L: the lattice basis
    :param delta: the delta parameter for LLL (default: 0.8)
    :return: the reduced basis
    """
    matrix_overview(L, 0)
    print(f"[+] Reducing a {L.nrows()} x {L.ncols()} lattice...")
    start_time = time.perf_counter()
    if USE_FLATTER:
        from subprocess import check_output
        from re import findall
        LL = "[[" + "]\n[".join(" ".join(map(str, row)) for row in L) + "]]"
        ret = check_output(["flatter"], input = LL.encode())
        L_reduced = matrix(L.nrows(), L.ncols(), map(int, findall(rb"-?\d+", ret)))
    else:
        L_reduced = L.LLL(delta)
    end_time = time.perf_counter()
    reduced_time = end_time - start_time
    print(f"[+] Reducing a {L.nrows()} x {L.ncols()} lattice within {reduced_time:.3f} seconds...")
    matrix_overview(L_reduced, 0.8)
    return L_reduced


def reconstruct_polynomials(B, f, modulus, monomials, bounds, preprocess_polynomial=lambda x: x, divide_gcd=True):
    """
    Reconstructs polynomials from the lattice basis in the monomials.
    :param B: the lattice basis
    :param f: the original polynomial (if set to None, polynomials will not be divided by f if possible)
    :param modulus: the original modulus
    :param monomials: the monomials
    :param bounds: the bounds
    :param preprocess_polynomial: a function which preprocesses a polynomial before it is added to the list (default: identity function)
    :param divide_gcd: if set to True, polynomials will be pairwise divided by their gcd if possible (default: True)
    :return: a list of polynomials
    """
    print(f"[+] Reconstructing polynomials (divide_original = {f is not None}, modulus_bound = {modulus is not None}, divide_gcd = {divide_gcd})...")
    polynomials = []
    for row in range(B.nrows()):
        norm_squared = 0
        w = 0
        polynomial = 0
        for col, monomial in enumerate(monomials):
            if B[row, col] == 0:
                continue
            norm_squared += B[row, col] ** 2
            w += 1
            assert B[row, col] % monomial(*bounds) == 0
            polynomial += B[row, col] * monomial // monomial(*bounds)

        # Equivalent to norm >= modulus / sqrt(w)
        if Bound_Check and modulus is not None and norm_squared * w >= modulus ** 2:
            print(f"[-] Row {row} is too large, ignoring...")
            continue

        polynomial = preprocess_polynomial(polynomial)

        if f is not None and polynomial % f == 0:
            print(f"[+] Original polynomial divides reconstructed polynomial at row {row}, dividing...")
            polynomial //= f

        if divide_gcd:
            for i in range(len(polynomials)):
                g = gcd(polynomial, polynomials[i])
                if g != 1 and g.is_constant():
                    print(f"[+] Reconstructed polynomial has gcd with polynomial at {i}, dividing...")
                    polynomial //= g
                    polynomials[i] //= g

        if polynomial.is_constant():
            print(f"[-] Polynomial at row {row} is constant, ignoring...")
            continue

        polynomials.append(polynomial)

    print(f"[+] Reconstructed {len(polynomials)} polynomials")
    return polynomials


def modular_bivariate_homogeneous(f, N, m, t, X, Y, roots_method="groebner"):
    """
    Computes small modular roots of a bivariate polynomial.
    More information: Lu Y. et al., "Solving Linear Equations Modulo Unknown Divisors: Revisited (Theorem 7)
    :param f: the polynomial
    :param N: the modulus
    :param m: the the parameter m
    :param t: the the parameter t
    :param X: an approximate bound on the x roots
    :param Y: an approximate bound on the y roots
    :param roots_method: the method to use to find roots (default: "groebner")
    :return: a generator generating small roots (tuples of x and y roots) of the polynomial
    """
    f = f.change_ring(ZZ)
    pr = PolynomialRing(ZZ, ['x', 'y'])
    x, y = pr.gens()

    al = int(f.coefficient(x))
    assert gcd(al, N) == 1
    f_ = (pow(al, -1, N) * f % N).change_ring(ZZ)

    print("[+] Generating shifts...")

    shifts = []
    for k in range(m + 1):
        g = y ** (m - k) * f_ ** k * N ** max(t - k, 0)
        shifts.append(g)

    L, monomials = create_lattice(pr, shifts, [X, Y])
    L = reduce_lattice(L)
    polynomials = reconstruct_polynomials(L, f, N ** t, monomials, [X, Y])
    start_time = time.perf_counter()
    t = var('t')
    g = polynomials[0].subs(x = t*y).subs(y = 1).simplify()
    print(f"[+] g = {truncate_int(g)}")
    root_t = solve(g == 0, t, domain = QQ)
    solutions = []
    for xy in root_t:  
        t0 = xy.rhs()
        x0 = t0.numerator()
        y0 = t0.denominator()
        root = {x: x0, y: y0}
        solutions.append(root)
    end_time = time.perf_counter()
    solution_time = end_time - start_time
    print(f"[+] Finding roots within {solution_time:.3f} seconds...")
    for roots in solutions:
        yield roots[x], roots[y]

def attack(p, h, xi1, xi2, s=5):
    """
    Attempts to recover (f, g) from p, h using a bivariate polynomial approach.
    Returns (x0, y0) if successful, else (None, None).
    """
    pr = ZZ["x", "y"]
    x, y = pr.gens()
    # The polynomial f(x,y) = x - h*y
    f_poly = x - h*y

    # Convert p to a real number, then raise to xi1, xi2
    X = int(RR(p)**xi1)
    Y = int(RR(p)**xi2)

    print(f"[+] Attempting s = {truncate_int(s)} (small roots approach) with X={truncate_int(X)}, Y={truncate_int(Y)}")

    for x0, y0 in modular_bivariate_homogeneous(f_poly, p, m=s, t=s, X=X, Y=Y):
        z = int(f_poly(x0, y0))
        x_int, y_int = ZZ(x0), ZZ(y0)
        if z % p == 0:
            assert (x_int - h*y_int) % p == 0
            print("[+] Found candidate root!")
            print(f"[+] x0 = {truncate_int(x_int)}\n[+] y0 = {truncate_int(y_int)}")
            
            return x_int, y_int
    return None, None

def decrypt_flag(ciphertext_hex, secret_int):
    secret_bytes = secret_int.to_bytes((secret_int.bit_length() + 7)//8, 'big')
    key = sha3_256(secret_bytes).digest()
    ciphertext_raw = bytes.fromhex(ciphertext_hex)
    iv = ciphertext_raw[:16]
    ct = ciphertext_raw[16:]

    # AES decryption
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ct), 16)
    return plaintext.decode('utf-8').strip()
def main():
    # 1) Attempt to find f, g
    start_time = time.perf_counter()
    print(f"[+] Starting attack with p = {truncate_int(p)}, h = {truncate_int(h)}, xi1 = {xi1}, xi2 = {xi2}, w = {w}")
    
    f_candidate, g_candidate = attack(p, h, xi1, xi2)
    if f_candidate is None or g_candidate is None:
        print("[-] No valid (f, g) found. Try adjusting parameters or a different strategy.")
        return
    
    print(f"[+] Recovered f = {truncate_int(f_candidate)}")
    print(f"[+] Recovered g = {truncate_int(g_candidate)}")
    # derive shared secret
    secret = (f_candidate * g_candidate) % p  
    print(f"[+] Derived AES key (int) = {truncate_int(secret)}")
    print(f"[+] Actual derived AES key (hex) = {sha3_256(secret.to_bytes((secret.bit_length() + 7)//8, 'big')).hexdigest()}")
    print(f"[+] Decrypting ciphertext...")
    flag = decrypt_flag(Ciphertext, secret)
    print(f"[+] Recovered Flag = {flag}")
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f"[+] Total time taken: {total_time:.3f} seconds")
    

if __name__ == "__main__":
    main()
