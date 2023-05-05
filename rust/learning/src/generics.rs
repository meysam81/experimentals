use std::fs::File;
use std::io::prelude::*;

// fn read_arr(idx: usize) -> Result<i32, &'static str> {
//     let arr = [1, 2, 3, 4, 5];
//     match arr.get(idx) {
//         Some(x) => Ok(*x),
//         None => Err("Index out of bounds"),
//     }
// }

// fn read_file(filename: &str) -> Result<String, &'static str> {
//     let mut f = match File::open(filename) {
//         Ok(file) => file,
//         Err(_) => Err("File not found"),
//     };
//     let mut s = String::new();
//     match f.read_to_string(&mut s) {
//         Ok(_) => Ok(s),
//         Err(_) => Err("File not found"),
//     }
// }

fn largest<T>(list: &[T]) -> &T {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let result = largest(&number_list);
    println!("The largest number is {}", result);

    let char_list = vec!['y', 'm', 'a', 'q'];

    let result = largest(&char_list);
    println!("The largest char is {}", result);
}
