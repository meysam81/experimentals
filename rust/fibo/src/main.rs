use std::collections::HashMap;
use std::env;

struct Fibo {
    cache: HashMap<u32, u64>,
}

impl Fibo {
    pub fn new() -> Self {
        let cache = HashMap::new();
        Self { cache: cache }
    }

    pub fn calc(&mut self, n: u32) -> u64 {
        let r: u64;
        if self.cache.contains_key(&n) {
            r = *self.cache.get(&n).unwrap();
        } else if n == 0 || n == 1 {
            r = n.into();
            self.cache.insert(n, r);
        } else {
            r = self.calc(n - 1) + self.calc(n - 2);
            self.cache.insert(n, r);
        };
        r
    }
}

fn fibo(n: u32) -> u64 {
    Fibo::new().calc(n)
}

fn main() {
    let mut f = Fibo::new();
    let n: u32 = env::args().nth(1).unwrap_or_else(|| String::from("8")).parse().unwrap();
    let s = f.calc(n);
    println!("{s:?}");
}

pub struct Guess {
    value: i32,
}

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!(
                "Guess value must be greater than or equal to 1, got {}.",
                value
            );
        } else if value > 100 {
            panic!(
                "Guess value must be less than or equal to 100, got {}.",
                value
            );
        }

        Guess { value }
    }

    pub fn value(&self) -> i32 {
        self.value
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "less than or equal to 100")]
    fn greater_than_100() {
        Guess::new(200);
    }
}

#[cfg(test)]
mod test_arithmetic {
    #[test]
    fn it_works() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}

#[cfg(test)]
mod test_fibo {
    use super::*;

    #[test]
    fn test_first_element_is_zero() {
        assert_eq!(fibo(0), 0);
    }

    #[test]
    fn test_second_element_is_one() {
        assert_eq!(fibo(1), 1);
    }

    #[test]
    fn test_third_until_tenth_element() {
        assert_eq!(fibo(2), 1);
        assert_eq!(fibo(3), 2);
        assert_eq!(fibo(4), 3);
        assert_eq!(fibo(5), 5);
        assert_eq!(fibo(6), 8);
        assert_eq!(fibo(7), 13);
        assert_eq!(fibo(8), 21);
        assert_eq!(fibo(9), 34);
        assert_eq!(fibo(10), 55);
    }

    #[test]
    fn test_ninety() {
        let n = 90;
        let rc = fibo(n);
        assert_eq!(rc, 2880067194370816120, "fibo({n}) = {rc}");
    }
}
