fn main() {
    let mut s: &'static str;
    {
        s = "hello world";
    }
    println!("{s:?}");
}