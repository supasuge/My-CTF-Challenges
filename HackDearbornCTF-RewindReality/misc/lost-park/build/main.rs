use std::io::{self, BufRead, BufReader, Write};

fn main() -> io::Result<()> {
    let mut attempts = 0;
    let max_attempts = 3;
    let correct_answer = "Aruba Park";

    let stdin = io::stdin();
    let mut stdout = io::stdout();
    let reader = BufReader::new(stdin.lock());

    writeln!(stdout, "Welcome to the lost park!")?;
    writeln!(stdout, "What is the name of the water park where the photo was taken?")?;
    writeln!(stdout, "You have {} attempts.", max_attempts)?;
    stdout.flush()?;

    for line in reader.lines() {
        let line = line?;
        attempts += 1;

        // Check if the input is correct (case-insensitive)
        if line.trim().eq_ignore_ascii_case(correct_answer) {
            writeln!(
                stdout,
                "Correct! Here is your flag: hd3{{this_guy_thinks_the_uc_is_named_after_him}}"
            )?;
            break;
        } else {
            writeln!(stdout, "Incorrect. Try again.")?;
        }

        if attempts >= max_attempts {
            writeln!(
                stdout,
                "You've used all {} attempts. Closing connection.",
                max_attempts
            )?;
            break;
        }

        writeln!(stdout, "Attempts remaining: {}", max_attempts - attempts)?;
        stdout.flush()?;
    }

    writeln!(stdout, "Goodbye!")?;
    Ok(())
}
