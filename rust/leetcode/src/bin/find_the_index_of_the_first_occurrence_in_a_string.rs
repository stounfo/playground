// https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
impl Solution {
    pub fn str_str(haystack: String, needle: String) -> i32 {
        return -1;
    }
}

struct Solution;

fn main() {
    assert!(Solution::str_str("sabsadbutsad".to_string(), "sad".to_string()) == 3);
    assert!(Solution::str_str("leetcode".to_string(), "eeee".to_string()) == -1);
}
