use std::fmt::Display;

fn longest_with_an_announcement<'a, T>(x: &'a str, y: &'a str, ann: T) -> &'a str
where
    T: Display,
{
    println!("Announcement! {}", ann);
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn main() {
    let s1 = &"Hello world!";
    let s2 = &"Hello again";
    let x = 14;
    let y =longest_with_an_announcement(s1, s2, x);
    println!("{y:?}");
}
