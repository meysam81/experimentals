fn fibo(n: u32) -> u32 {
    if n == 0 || n == 1 {
        n
    } else {
        fibo(n - 1) + fibo(n - 2)
    }
}

// 0 1 1 2 3 5 8 13 21 34 55 89

#[cfg(test)]
mod tests {
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
}
