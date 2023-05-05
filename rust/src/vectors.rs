pub fn vec_() {
    let v = vec![1, 2, 3, 4, 5];

    let third: &i32 = &v[2];
    println!("The third element is {third}");

    if let Some(third) = v.get(3) {
        println!("The third element is {third:?}");
    }
}

pub fn vec_borrow() {
    let mut v = vec![1, 2, 3, 4, 5];

    let first = &v[0];

    println!("The first element is: {first}");
    v.push(6);
}

pub fn vec_iterate() {
    let v = vec![100, 32, 57];
    for i in &v {
        println!("{i}");
    }
}

pub fn vec_iterate_mut() {
    let mut v = vec![100, 32, 57];
    for i in &mut v {
        *i += 50;
    }
    println!("{v:?}");
}

pub fn vec_types() {
    #[derive(Debug)]
    enum SpreadsheetCell {
        Int(i32),
        Float(f64),
        Text(String),
    }

    let row = vec![
        SpreadsheetCell::Int(3),
        SpreadsheetCell::Text(String::from("blue")),
        SpreadsheetCell::Float(10.12),
    ];

    println!("{row:?}");
}
