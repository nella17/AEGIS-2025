# Self-Assignment Analysis: String vs Bitmap

## Test Results Comparison

### String Self-Assignment
```bitscript
string s1 = "test";
s1 = s1;
print(s1);  // Prints nothing (corrupted)
```
**Result:** Value corrupted, use-after-free confirmed

### Bitmap Self-Assignment
```bitscript
bitmap b1 = create(10, 10);
set(b1, 0, 0, 1);
b1 = b1;
int val = get(b1, 0, 0);  // Returns 1 (still works!)
delete(b1);  // No crash
```
**Result:** Value still accessible, no crash

## Why the Difference?

### Memory Layout

**String Structure:**
```
Offset 0x00: length (QWORD)
Offset 0x08: data pointer (char*)
```

**Bitmap Structure:**
```
Offset 0x00: width (QWORD)
Offset 0x08: height (QWORD)
Offset 0x10: data pointer (byte*)
```

### What Happens During Self-Assignment

**For Strings (`s1 = s1;`):**
```c
1. eval_expression(s1) → Returns pointer to s1's string struct (v5)
2. Check: if (s1.value_ptr exists) {
     free(s1.value_ptr->data);      // Free string data
     free(s1.value_ptr);             // Free string struct
   }
3. s1.value_ptr = v5;  // Set to freed pointer!
```

**For Bitmaps (`b1 = b1;`):**
```c
1. eval_expression(b1) → Returns pointer to b1's bitmap struct (v5)
2. Check: if (b1.value_ptr exists) {
     free(b1.value_ptr->data);      // Free bitmap data (offset 0x10)
     free(b1.value_ptr);             // Free bitmap struct
   }
3. b1.value_ptr = v5;  // Set to freed pointer!
```

## Why Bitmap Still Works?

**Possible Explanations:**

### 1. Freed Memory Not Yet Reused
- The freed bitmap struct and data haven't been reused by `malloc` yet
- The memory still contains the original data
- `get(b1, 0, 0)` reads from freed memory, but it still has valid data
- **This is still Use-After-Free!** Just the memory hasn't been corrupted yet

### 2. Delete Function Protection
- `delete(b1)` might check if the pointer is already freed
- Or it might check if the bitmap data pointer is NULL
- But looking at the code, `delete` doesn't seem to have such checks

### 3. Tcache Behavior
- Modern glibc uses tcache (thread-local cache) for freed chunks
- Freed chunks in tcache might still be readable
- But they shouldn't be freed again (would cause double free)
- Maybe `delete` doesn't actually try to free if it's already in tcache?

## The Real Issue

**Both are Use-After-Free vulnerabilities:**

1. **String:** Memory gets corrupted quickly (maybe reused faster)
2. **Bitmap:** Memory still readable (not yet reused), but still **freed memory**

**Both are dangerous:**
- Reading from freed memory → Use-After-Free
- Writing to freed memory → Heap corruption
- Freeing again → Double Free (if memory is reused)

## Why Delete Doesn't Crash

**Possible reasons:**

1. **Memory already in tcache:** The freed chunk is in tcache, and `free()` might handle it differently
2. **Pointer validation:** `delete` might check if the bitmap data pointer is valid before freeing
3. **Lucky timing:** The freed memory hasn't been reused, so `free()` doesn't detect double free yet

**But this is still a vulnerability!** The memory is freed, and accessing it is undefined behavior.

## Exploitation Potential

**Use-After-Free can lead to:**
1. **Information Leak:** Read sensitive data from freed memory
2. **Heap Corruption:** Write to freed memory that gets reused
3. **Double Free:** If freed memory is reused, then freed again
4. **RCE:** Through heap exploitation techniques

## Conclusion

**Self-assignment creates Use-After-Free in both cases:**
- ✅ String: Value corrupted (memory reused/corrupted)
- ⚠️ Bitmap: Value still readable (memory not yet reused), but still **freed**

**Both are exploitable vulnerabilities!**

