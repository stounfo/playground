// https://leetcode.com/problems/length-of-last-word/description/
impl Solution {
    pub fn length_of_last_word(s: String) -> i32 {
        let mut start = s.len();
        for i in (0..s.len()).rev() {
            if s.as_bytes()[i] != b' ' {
                start = i + 1;
                break;
            };
        }
        for i in (0..start).rev() {
            if s.as_bytes()[i] == b' ' {
                return (start - 1 - i) as i32;
            }
        }
        return start as i32;
    }
}

struct Solution;

fn main() {
    assert!(Solution::length_of_last_word("Hello World".to_string()) == 5);
    assert!(Solution::length_of_last_word("   fly me   to   the moon  ".to_string()) == 4);
    assert!(Solution::length_of_last_word("luffy is still joyboy".to_string()) == 6);
    assert!(Solution::length_of_last_word("a ".to_string()) == 1);
    assert!(Solution::length_of_last_word("a".to_string()) == 1);
    assert!(Solution::length_of_last_word("allah".to_string()) == 5);
}
