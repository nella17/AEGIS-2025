# All Double Free Vulnerabilities

## Summary

Found **3 different double free/use-after-free vulnerabilities** in the bitscript interpreter:

1. ✅ **String Assignment Double Free** (CONFIRMED)
2. ✅ **Bitmap Assignment Double Free** (CONFIRMED)
3. ⚠️ **Self-Assignment Use-After-Free** (CONFIRMED, Double Free Unconfirmed)

## 1. String Assignment Double Free ✅ CONFIRMED

**Location:** `eval_statement`, case 4 (ASSIGNMENT), lines 66-76

**Root Cause:** String assignment does shallow copy (pointer copy), not deep copy.

**Trigger:**
```bitscript
string s1 = "first";
string s2 = "second";
s2 = s1;  // Both point to same struct
// Cleanup or delete both → DOUBLE FREE!
```

**Status:** ✅ **CONFIRMED** - Crashes with "double free or corruption (!prev)"

**Files:**
- `poc_double_free.bs`
- `poc_double_free_reassign.bs`
- `poc_double_free_cleanup.bs`

## 2. Bitmap Assignment Double Free ✅ CONFIRMED

**Location:** `eval_statement`, case 4 (ASSIGNMENT), lines 71-76

**Root Cause:** Bitmap assignment does shallow copy (pointer copy), same as strings.

**Trigger:**
```bitscript
bitmap b1 = create(10, 10);
bitmap b2 = create(20, 20);
b2 = b1;  // Both point to same struct
delete(b2);
delete(b1);  // → DOUBLE FREE!
```

**Status:** ✅ **CONFIRMED** - Crashes with "free(): double free detected in tcache 2"

**Files:**
- `poc_double_free_bitmap.bs`
- `double_free_bitmap_analysis.md`

## 3. Self-Assignment Use-After-Free ⚠️ CONFIRMED (Double Free Unconfirmed)

**Location:** `eval_statement`, case 4 (ASSIGNMENT), lines 66-76

**Root Cause:** No check for self-assignment. Frees old value, then sets pointer to same freed pointer.

**Trigger:**
```bitscript
string s1 = "test";
s1 = s1;  // Frees s1's string, then sets s1.value_ptr to freed pointer
print(s1);  // Use-After-Free! (prints nothing/corrupted)
// Cleanup might try to free again → DOUBLE FREE?
```

**What happens:**
1. `eval_expression(s1)` returns pointer to s1's string struct
2. Code frees s1's old string (the same struct!)
3. Sets `s1.value_ptr = freed_pointer`
4. `print(s1)` reads from freed memory → **Use-After-Free!**
5. Cleanup might try to free again → **Potential DOUBLE FREE!**

**Status:** ⚠️ **PARTIAL** - Use-After-Free confirmed, double free during cleanup needs testing

**Test Results:**
- After `s1 = s1;`, `print(s1)` prints nothing (value corrupted)
- Script completes without crash (freed memory not yet reused)
- Need to test cleanup scenario

**Files:**
- `poc_double_free_self_assignment.bs`
- `poc_self_assignment_cleanup.bs` (to test cleanup)
- `poc_self_assignment_bitmap.bs` (bitmap version)
- `double_free_self_assignment_analysis.md`

## Common Pattern

All three vulnerabilities share the same root cause:

**Assignment code doesn't:**
1. Check for self-assignment
2. Create deep copies (for strings/bitmaps)
3. Track reference counts

**Assignment code does:**
1. Free old value unconditionally
2. Copy pointer (shallow copy)
3. No checks for shared references

## Exploitation Value

All three can lead to:
- **Heap Corruption** - Corrupts heap metadata
- **Fastbin/Tcache Attack** - Control next allocation
- **Arbitrary Write** - Write to controlled address
- **RCE** - Overwrite GOT → system() → shell

## Next Steps

1. ✅ Test string assignment double free (CONFIRMED)
2. ⏳ Test bitmap assignment double free
3. ⏳ Test self-assignment double free
4. ⏳ Exploit one or more for RCE

