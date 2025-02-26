// https://leetcode.com/problems/plus-one/description/
impl Solution {
    pub fn plus_one(digits: Vec<i32>) -> Vec<i32> {
        let mut first_nine: Option<usize> = None;
        for i in (0..digits.len()).rev() {
            if digits[i] == 9 {
                first_nine = Some(i);
            } else {
                break;
            }
        }
        return match first_nine {
            None => {
                let mut final_digits = digits.clone();
                let last_index = final_digits.len() - 1;
                final_digits[last_index] += 1;
                final_digits
            }
            Some(0) => {
                let mut final_digits = vec![1; digits.len() + 1];
                final_digits[1..].fill(0);
                final_digits
            }
            _ => {
                let mut final_digits = digits.clone();
                final_digits[first_nine.unwrap() - 1] += 1;
                final_digits[first_nine.unwrap()..].fill(0);
                final_digits
            }
        };
    }
}

struct Solution;

fn main() {
    assert!(Solution::plus_one(vec![9, 9, 9]) == vec![1, 0, 0, 0]);
    assert!(Solution::plus_one(vec![9, 7, 9]) == vec![9, 8, 0]);
    assert!(Solution::plus_one(vec![9, 7, 9, 9, 9]) == vec![9, 8, 0, 0, 0]);
    assert!(Solution::plus_one(vec![1, 2, 3]) == vec![1, 2, 4]);
    assert!(Solution::plus_one(vec![4, 3, 2, 1]) == vec![4, 3, 2, 2]);
}
