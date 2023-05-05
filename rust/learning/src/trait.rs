trait Summary {
    fn summarize(&self);
}

struct MyStruct {
    name: String,
    age: u32,
    numbers: Vec<u32>,
}

impl MyStruct {
    pub fn new(name: String, age: u32, numbers: Vec<u32>) -> Self {
        MyStruct { name, age, numbers }
    }

    pub fn numbers(&self) -> &Vec<u32> {
        &self.numbers
    }
}

impl Summary for MyStruct {
    fn summarize(&self) {
        println!(
            "name={} age={} numbers={:?}",
            self.name, self.age, self.numbers
        );
    }
}

fn main() {
    let m = MyStruct::new("John".to_string(), 30, vec![1, 2, 3]);
    m.summarize();
    for n in m.numbers().iter() {
        println!("{}", *n);
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn iterator_demonstration() {
        let v1 = vec![1, 2, 3];

        let mut v1_iter = v1.iter();

        assert_eq!(v1_iter.next(), Some(&1));
        assert_eq!(v1_iter.next(), Some(&2));
        assert_eq!(v1_iter.next(), Some(&3));
        assert_eq!(v1_iter.next(), None);
        assert_eq!(v1_iter.next(), None);
    }

    #[test]
    fn iter_mut() {
        let mut v1 = vec![1, 2, 3];
        let mut v1_iter = v1.iter_mut();

        let mut r = v1_iter.next().unwrap();
        *r += 1;

        println!("{:?}", v1);
        assert!(false);
    }

    #[test]
    fn iterator_sum() {
        let v1 = vec![1, 2, 3];

        let v1_iter = v1.iter();

        let total: i32 = v1_iter.sum();
        println!("{:?}", v1_iter);
        // assert!(false);
    }
}

impl Config {
    pub fn build(mut args: impl Iterator<Item = String>) -> Result<Config, &'static str> {
        args.next();

        let query = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a query string"),
        };

        let file_path = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a file path"),
        };

        let ignore_case = env::var("IGNORE_CASE").is_ok();

        Ok(Config {
            query,
            file_path,
            ignore_case,
        })
    }
}
