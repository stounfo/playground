use std::io;

struct User {
    given_name: String,
    family_name: String,
}

enum GetUserError {
    ConnectionError,
    NotFound,
}

fn get_user(id: u32) -> Result<User, GetUserError> {
    return match id {
        1 => Ok(User {
            given_name: String::from("Viktor"),
            family_name: String::from("Tsoy"),
        }),
        4 => Err(GetUserError::ConnectionError),
        _ => Err(GetUserError::NotFound),
    };
}

fn main() {
    loop {
        println!("Please input user_id ");
        let mut user_id = String::new();
        io::stdin()
            .read_line(&mut user_id)
            .expect("Failed to read line");

        let user_id: u32 = match user_id.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        match get_user(user_id) {
            Ok(user) => {
                let user = user;
                println!("User found: {} {}", user.given_name, user.family_name);
            }
            Err(GetUserError::ConnectionError) => println!("Connection Error"),
            Err(GetUserError::NotFound) => println!("User doesn't exist"),
        }
        println!("\n");
    }
}
