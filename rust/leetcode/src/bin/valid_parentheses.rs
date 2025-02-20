// https://leetcode.com/problems/valid-parentheses/
use std::collections::HashMap;
use std::collections::VecDeque;

impl Solution {
    pub fn is_valid(s: String) -> bool {
        let mut hash = HashMap::new();
        let mut deque = VecDeque::new();
        hash.insert(']', '[');
        hash.insert(')', '(');
        hash.insert('}', '{');

        for ch in s.chars() {
            if matches!(ch, '[' | '{' | '(') {
                deque.push_front(ch);
            } else {
                if deque.len() == 0 {
                    return false;
                }
                let prev = deque.pop_front().unwrap();
                if hash.get(&ch).unwrap() != &prev {
                    return false;
                }
            };
        }
        if deque.len() == 0 {
            return true;
        }
        return false;
    }
}

struct Solution;

fn main() {
    assert!(Solution::is_valid(String::from("()")));
    assert!(Solution::is_valid(String::from("([])")));
    assert!(Solution::is_valid(String::from("()[]{}")));
    assert!(!Solution::is_valid(String::from("([)]")));
    assert!(!Solution::is_valid(String::from("((")));
    assert!(!Solution::is_valid(String::from("][")));
    assert!(!Solution::is_valid(String::from("){")));
    assert!(!Solution::is_valid(String::from("()){")));
    assert!(!Solution::is_valid(String::from("({{{{}}}))")));
    assert!(Solution::is_valid(String::from("{{}}")));
    assert!(!Solution::is_valid(String::from("(){(())}}{")));
    assert!(Solution::is_valid(String::from("(([]){})")));
    assert!(Solution::is_valid(String::from("(([])){(())}[]")));
}
