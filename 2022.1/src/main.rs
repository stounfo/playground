use std::fs::File;
use std::io::{self, prelude::*, BufReader};

fn main() -> io::Result<()> {
    let file = File::open("data")?;
    let mut buf_reader = BufReader::new(file);
    let mut data = String::new();

    buf_reader.read_to_string(&mut data)?;


    let mut max = 0;
    for part in data.split("\n\n") {
        let mut sum: i32 = 0;
        for i in part.split("\n") {
            let step: i32 = match i.trim().parse() {
                Ok(num) => num,
                Err(_) => continue,
            };
            sum += step;

        }
        if max <= sum {
            max = sum;
        }
    }

    println!("{max}");

    Ok(())
}
