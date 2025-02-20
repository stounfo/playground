// https://leetcode.com/problems/remove-element/
impl Solution {
    pub fn remove_element(nums: &mut Vec<i32>, val: i32) -> i32 {
        let mut j = 0;
        for i in 0..nums.len() {
            if nums[i] != val {
                nums[j] = nums[i];
                j += 1;
            }
        }
        return j as i32;
    }
}

struct Solution;

fn main() {
    assert!(Solution::remove_element(&mut vec![3, 2, 2, 3], 3) == 2);
    assert!(Solution::remove_element(&mut vec![0, 1, 2, 2, 3, 0, 4, 2], 2) == 5);
}
