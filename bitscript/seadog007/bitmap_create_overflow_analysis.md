# Bitmap Create Overflow - Deep Analysis

## Code at 0x401AEB

```c
bitmap_create(__int64 a1, __int64 a2) {
    // Line 6: Bounds check
    if ( a1 <= 0 || a2 <= 0 || a2 * a1 > 0x800000 )
        exit(1);
    
    // Line 19: Calculate size
    v2 = a2 * a1 + 7;
    
    // Line 20: Overflow check (AFTER calculation!)
    if ( v2 < 0 )
        v2 = a2 * a1 + 14;
    
    // Line 22: Allocate
    v4[2] = malloc((int)(v2 >> 3));
}
```

## The Critical Overflow

**Line 6:** `a2 * a1 > 0x800000`

**The Bug:** The multiplication `a2 * a1` can **OVERFLOW IN THE CHECK ITSELF**!

### Signed Integer Overflow in Check

In **signed 64-bit arithmetic**, if:
- `a1` and `a2` are large enough
- `a2 * a1` overflows and wraps to a **negative number**
- Then: `negative_number > 0x800000` = **FALSE**
- Check **PASSES incorrectly**!

### Example Values

**To trigger signed overflow:**
- Need: `a1 * a2` > `INT64_MAX` (0x7FFFFFFFFFFFFFFF)
- But then it wraps to negative
- Negative < 0x800000, so check passes!

**Example:**
- `a1 = 0x100000000` (4,294,967,296)
- `a2 = 0x2000000` (33,554,432)  
- `a1 * a2` = would overflow in signed arithmetic
- If it wraps to negative, check passes!

### The Exploitation Path

1. **Find values where `a2 * a1` overflows in signed arithmetic**
2. **Overflow wraps to negative or small positive**
3. **Check `a2 * a1 > 0x800000` passes (negative is not > 0x800000)**
4. **Line 19:** `v2 = a2 * a1 + 7` uses overflowed value
5. **Line 22:** `malloc((int)(v2 >> 3))` allocates wrong size
6. **Subsequent operations:** Out-of-bounds access → RCE

## Testing

Need to find values where:
- `a1 * a2` overflows in signed 64-bit
- But passes the check `a2 * a1 > 0x800000`

This is different from the string concatenation overflow - this one might be more exploitable!

