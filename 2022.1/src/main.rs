use std::fs::File;
use std::io::{self, prelude::*, BufReader};

fn main() -> io::Result<()> {
    let file = File::open("data")?;
    let mut buf_reader = BufReader::new(file);
    let mut data = String::new();

    buf_reader.read_to_string(&mut data)?;

    let max = data
        .split("\n\n")
        .filter_map(|part| {
            part.split("\n")
                .map(|i| i.trim().parse::<i32>())
                .filter_map(Result::ok)
                .sum::<i32>()
                .checked_sub(1)
        })
        .max();

    match max {
        Some(m) => println!("{m}"),
        None => println!("No data found"),
    }

    Ok(())
}
