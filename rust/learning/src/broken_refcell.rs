use std::cell::RefCell;

fn main() {
    let x = RefCell::new(42);

    // Borrow a mutable reference to the inner value
    let mut y = x.borrow_mut();

    // Attempt to borrow a shared reference to the inner value
    let z = x.borrow();
    println!("z: {}", *z);
}
