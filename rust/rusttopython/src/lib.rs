use pyo3::prelude::*;

#[pyfunction]
fn calc_something(n: i32) -> PyResult<Vec<i32>> {
    let mut primes = Vec::new();
    'outer: for candidate in 2..=n {
        for divisor in 2..= ((candidate as f64).sqrt() as i32 + 1) {
            if candidate % divisor == 0 {
                continue 'outer;
            }
        }
        primes.push(candidate);
    }
    Ok(primes)
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn test_test(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calc_something, m)?)?;

    Ok(())
}
