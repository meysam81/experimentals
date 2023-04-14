use std::collections::HashMap;

#[derive(Debug)]
enum MyEnum {
    Int(i32),
    Float(f64),
    Str(String),
}

fn hash_insert() {
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);
    // scores.insert("Yellow1", 50);
    // scores.insert(MyEnum::Str(String::from("Yellow2")), 50);

    println!("{scores:?}");
}

fn hash_get() {
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    let team_name = String::from("Blue1");
    let score = scores.get(&team_name).copied().unwrap_or(0);

    println!("{scores:?}");
    println!("team_name: {team_name:?}");
    println!("score: {score:?}");
}

fn hash_iter() {
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    for (key, value) in &scores {
        println!("{key}: {value}");
    }
}

fn hash_overwrite() {
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Blue"), 25);

    println!("{:?}", scores);
}

fn hash_upsert() {
    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);

    scores.entry(String::from("Yellow")).or_insert(50);
    scores.entry(String::from("Blue")).or_insert(50);

    println!("{:?}", scores);
}

fn hash_update() {
    let text = "hello world wonderful world";

    let mut map = HashMap::new();

    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }

    println!("{:?}", map);
}
