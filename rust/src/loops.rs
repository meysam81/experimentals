pub fn for_loop() {
    for i in 1..=3 {
        println!("{i}")
    }
}

pub fn while_loop() {
    let mut i = 1;
    while i <= 3 {
        println!("{i}");
        i += 1;
    }
}

pub fn loop_() {
    let mut i = 1;
    loop {
        println!("{i}");
        i += 1;
        if i > 3 {
            break;
        }
    }
}