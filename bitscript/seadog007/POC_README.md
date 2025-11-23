# Proof of Concept Scripts for Bitscript Interpreter Vulnerabilities

This directory contains proof-of-concept scripts demonstrating various vulnerabilities found in the bitscript interpreter.

## Files

### 1. `poc_bitmap_create_overflow.bs`
**Vulnerability**: Integer overflow in `bitmap_create()` function  
**Severity**: CRITICAL  
**Description**: 
- Creates a bitmap with dimensions 65536x65536
- The multiplication `65536 * 65536 = 0x100000000` wraps to `0` in 64-bit arithmetic
- This bypasses the bounds check (`0 > 0x800000` is false)
- Allocates a tiny buffer instead of the expected large one
- Subsequent `set()`/`get()` operations write/read out of bounds

**Usage**:
```bash
./bitscript poc_bitmap_create_overflow.bs
```

**Expected Result**: Heap corruption, potential crash or RCE

---

### 2. `poc_bitmap_create_overflow_v2.bs`
**Vulnerability**: Integer overflow in `bitmap_create()` - alternative values  
**Severity**: CRITICAL  
**Description**: 
- Alternative approach using different values that cause overflow
- Tries multiple combinations: 4096x1048576, 8192x524288, etc.
- Demonstrates the vulnerability with different overflow scenarios

**Usage**:
```bash
./bitscript poc_bitmap_create_overflow_v2.bs
```

---

### 3. `poc_substr_overflow.bs`
**Vulnerability**: Integer overflow in `substr()` bounds check  
**Severity**: HIGH  
**Description**:
- Attempts to use maximum int64 value (9223372036854775807) as start position
- When added to length, the sum can overflow
- The bounds check `(unsigned)(start + length) > string_length` can be bypassed
- Allows reading from arbitrary memory locations

**Usage**:
```bash
./bitscript poc_substr_overflow.bs
```

**Expected Result**: Out-of-bounds read, potential information disclosure

**Note**: May require specific conditions to fully exploit, as the bounds check might still catch some cases.

---

### 4. `poc_replace_overflow.bs`
**Vulnerability**: Integer overflow in `replace()` bounds check  
**Severity**: HIGH  
**Description**:
- Attempts to use maximum int64 value as position
- When position + replacement_length overflows, bounds check can be bypassed
- Allows writing to arbitrary memory locations via `memcpy()`

**Usage**:
```bash
./bitscript poc_replace_overflow.bs
```

**Expected Result**: Out-of-bounds write, heap corruption

**Note**: May require specific conditions to fully exploit.

---

### 5. `poc_bitmap_index_overflow.bs`
**Vulnerability**: Missing overflow check in bitmap index calculation  
**Severity**: MEDIUM  
**Description**:
- Demonstrates that `bitmap_set()` and `bitmap_get()` don't check for overflow
- The calculation `y * width + x` can overflow even when x and y are in bounds
- This can lead to accessing wrong memory locations

**Usage**:
```bash
./bitscript poc_bitmap_index_overflow.bs
```

**Note**: This POC is more complex as it requires bypassing the bounds check first, then triggering the index overflow. The bitmap creation overflow (POC 1) might be a prerequisite.

---

### 6. `poc_string_concat_overflow.bs`
**Vulnerability**: Integer overflow in string concatenation  
**Severity**: MEDIUM  
**Description**:
- String concatenation doesn't check if `len1 + len2` overflows
- When it overflows, allocates wrong buffer size
- Can lead to buffer overflow when copying strings

**Usage**:
```bash
./bitscript poc_string_concat_overflow.bs
```

**Note**: This is harder to exploit directly from bitscript code because:
- String literals are limited to 255 bytes
- Would require manipulating internal string length fields
- May need a secondary vulnerability to fully exploit

---

### 7. `poc_all_vulnerabilities.bs`
**Vulnerability**: Combined demonstration of all vulnerabilities  
**Description**: 
- Attempts to trigger all vulnerabilities in sequence
- Useful for testing multiple attack vectors at once

**Usage**:
```bash
./bitscript poc_all_vulnerabilities.bs
```

---

## Running the POCs

### Prerequisites
- The bitscript interpreter binary (`bitscript`)
- Access to run the interpreter

### Basic Usage
```bash
# Run a single POC
./bitscript poc_bitmap_create_overflow.bs

# Or if bitscript is in a different location
/path/to/bitscript poc_bitmap_create_overflow.bs
```

### Expected Behavior

**Successful Exploitation**:
- Heap corruption
- Segmentation fault
- Potential code execution (depending on mitigations)
- Out-of-bounds memory access

**Failed Exploitation**:
- Error messages from bounds checks
- Program exit with error
- No crash (if bounds checks prevent the issue)

## Notes

1. **Some POCs may not trigger immediately**: Due to bounds checking, some vulnerabilities require specific conditions or multiple steps to exploit.

2. **The bitmap_create overflow is the most reliable**: This is the most critical and easiest to trigger vulnerability.

3. **Environment matters**: Results may vary depending on:
   - Compiler optimizations
   - ASLR (Address Space Layout Randomization)
   - Stack canaries
   - Other security mitigations

4. **Use in controlled environment**: These POCs are for security research and testing only. Do not use on production systems.

## Mitigation Recommendations

1. Add overflow checks before all multiplications
2. Use `__builtin_mul_overflow` or similar compiler intrinsics
3. Validate all arithmetic operations for overflow
4. Use safe integer libraries
5. Add bounds checking on all array/pointer arithmetic
6. Implement comprehensive fuzzing

## References

See `vulnerabilities.txt` for detailed technical analysis of each vulnerability.

