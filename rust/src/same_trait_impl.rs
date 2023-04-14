trait Foo {
    fn baz(&self) -> i32;
}

trait Bar {
    fn baz(&self) -> i32;
}

struct MyStruct;

impl Foo for MyStruct {
    fn baz(&self) -> i32 {
        42
    }
}

impl Bar for MyStruct {
    fn baz(&self) -> i32 {
        99
    }
}

fn main() {
    let my_struct = MyStruct;
    let result = Bar::baz(&my_struct); // result is 42 (the result of the Foo implementation)
    println!("{:?}", result)
}
