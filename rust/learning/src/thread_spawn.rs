use std::thread;
use std::time::Duration;

fn mythread() {
    for i in 1..10 {
        println!("hi number {} from the spawned thread!", i);
        thread::sleep(Duration::from_millis(1));
    }
}

fn main() {
    let t = thread::spawn(mythread);

    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }

    t.join().unwrap();
}
