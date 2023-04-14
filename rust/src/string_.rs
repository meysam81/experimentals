fn string_init() {
    let mut s = String::new();

    println!("s: {s:?}");

    s = String::from("abcdABCD");

    println!("s: {s:?}");

    println!("s.len(): {}", s.len());
    println!("b's: {:?}", s.bytes());
}

fn string_push() {
    let mut s = "hello world".to_string();
    println!("s: {s:?}");

    s.push_str(", how are you?");
    println!("s: {s:?}");

    s = String::from("سلام چطوری؟");
    println!("s: {s:?}");
}

fn string_concat1() {
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");
    let s3 = s1 + &s2; // note s1 has been moved here and can no longer be used

    // println!("s1: {s1:?}"); // compile error (borrow of moved value: `s1`)
    println!("s2: {s2:?}");
    println!("s3: {s3:?}");
}

fn string_concat2() {
    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");

    let s = s1 + "-" + &s2 + "-" + &s3;

    println!("s: {s:?}");
    // println!("s1: {s1:?}"); // compile error (borrow of moved value: `s1`)
    println!("s2: {s2:?}");
    println!("s3: {s3:?}");
}

fn string_concat3() {
    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");

    let s = format!("{s1}-{s2}-{s3}");

    println!("s: {s:?}");
    println!("s1: {s1:?}");
    println!("s2: {s2:?}");
    println!("s3: {s3:?}");
}

fn string_iter() {
    for c in "Здравствуйте".chars() {
        println!("{c}");
    }

    for c in "नमस्ते".chars() {
        println!("{c}");
    }
}

fn string_contains() {
    let s = "hello world";
    println!("s: {s:?}");
    // let c = s.contains("world");
    println!("contains: {}, {}", s.contains("world"), s.contains("dummy"));
}

fn string_replace() {
    let s = "hello world";
    println!("s: {s:?}");
    let s = s.replace("world", "rust");
    println!("s: {s:?}");
}
