trait Speak {
    fn speak(&self) -> &'static str;
}

struct Person {
    name: String,
}

impl Speak for Person {
    fn speak(&self) -> &'static str {
        "Hello, my name is "
    }
}

struct Robot {
    id: i32,
}

impl Speak for Robot {
    fn speak(&self) -> &'static str {
        "I am a robot with id "
    }
}

fn main() {
    let mut vec: Vec<Box<dyn Speak>> = Vec::new();
    vec.push(Box::new(Person {
        name: "Alice".into(),
    }));
    vec.push(Box::new(Robot { id: 42 }));

    for speakable in vec {
        println!("{}", speakable.speak());
    }
}
