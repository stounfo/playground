// https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/
impl Solution {
    pub fn remove_duplicates(nums: &mut Vec<i32>) -> i32 {
        let mut j = 1;
        for i in 1..nums.len() {
            if nums[i] != nums[i - 1] {
                nums[j] = nums[i];
                j += 1;
            };
        }
        return j as i32;
    }
}

struct Solution;

fn main() {
    assert!(Solution::remove_duplicates(&mut vec![1, 1, 1, 2, 2]) == 2);
    assert!(Solution::remove_duplicates(&mut vec![0, 0, 1, 1, 1, 2, 2, 3, 3, 4]) == 5);
    assert!(
        Solution::remove_duplicates(&mut vec![
            0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4
        ]) == 5
    );
}
