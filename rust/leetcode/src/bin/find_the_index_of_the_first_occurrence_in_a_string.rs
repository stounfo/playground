// https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
impl Solution {
    pub fn str_str(haystack: String, needle: String) -> i32 {
        if haystack.len() < needle.len() {
            return -1;
        };
        for i in 0..haystack.len() {
            let mut j = 0;
            let mut is_equal = true;
            while is_equal && j + i < haystack.len() {
                if haystack.chars().nth(i + j).unwrap() != needle.chars().nth(j).unwrap() {
                    is_equal = false;
                };
                j += 1;
                if j == needle.len() && is_equal == true {
                    return i as i32;
                }
            }
        }
        return -1;
    }
}

struct Solution;

fn main() {
    assert!(Solution::str_str("sabsadbutsad".to_string(), "sad".to_string()) == 3);
    assert!(Solution::str_str("leetcode".to_string(), "eeee".to_string()) == -1);
    assert!(Solution::str_str("a".to_string(), "a".to_string()) == 0);
    assert!(Solution::str_str("aaa".to_string(), "aaaa".to_string()) == -1);
    assert!(Solution::str_str("mississippi".to_string(), "issipi".to_string()) == -1);
}
