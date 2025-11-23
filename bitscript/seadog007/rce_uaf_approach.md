# RCE via Use-After-Free Approach

## Why Bitmap Overflow Doesn't Work

**Problem:** Bitmap overflow requires `x < 8`, but for nearby addresses:
- `offset = 7464 bytes`
- `bit_offset = 59712 bits`
- `x = 59712 % 8 = 0` ✅
- But `y = 59712 / INT64_MAX = 0` ❌

This writes to `bitmap_data_ptr + 0`, not to `value_ptr_addr`!

**Solution:** Use Use-After-Free instead!

## Use-After-Free Exploit Strategy

### Step 1: Create Use-After-Free
```bitscript
string target = "dummy";
target = target;  // Creates use-after-free
// target.value_ptr now points to freed memory
```

### Step 2: Heap Grooming
```bitscript
// Allocate objects that will reuse the freed memory
// Goal: Make target.value_ptr point to another variable's entry
```

### Step 3: Corrupt Variable Entry
```bitscript
// If target.value_ptr points to another variable's entry,
// we can read/write that entry through target
// Corrupt its value_ptr to point to printf@GOT
```

### Step 4: Leak Libc
```bitscript
// Read from corrupted variable (now points to printf@GOT)
int libcprintf = corrupted_var;
```

### Step 5: Overwrite GOT
```bitscript
// Use use-after-free again to write system() address
// Or use bitmap overflow if we can get larger offset
```

## Alternative: Find Bitmap Buffer Location

Maybe the bitmap buffer is allocated at a different location. Let's try to find it using OOB read.

