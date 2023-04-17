trait Animal {
    fn make_sound(&self);
}

struct Dog;
impl Animal for Dog {
    fn make_sound(&self) {
        println!("Woof!");
    }
}

struct Cat;
impl Animal for Cat {
    fn make_sound(&self) {
        println!("Meow!");
    }
}

fn create_animal(kind: &str) -> Box<dyn Animal> {
    match kind {
        "cat" => Box::new(Cat {}),
        "dog" => Box::new(Dog {}),
        _ => panic!("Unknown animal type"),
    }
}

fn create_animal1() -> impl Animal {
    Dog {}
}

fn create_animal2() -> impl Animal {
    Cat {}
}

fn main() {
    let animal1 = create_animal1();
    let animal2 = create_animal2();
    let animal3 = create_animal(&"cat");
    let animal4 = create_animal(&"dog");

    // Call method on trait objects
    animal1.make_sound(); // prints "Woof!"
    animal2.make_sound(); // prints "Meow!"
    animal3.make_sound(); // prints "Meow!"
    animal4.make_sound(); // prints "Woof!"
}
