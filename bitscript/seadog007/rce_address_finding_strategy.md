# Address Finding Strategy for RCE

## The Challenge

We need to find:
1. **Variable entry address** - Where `target` variable's entry is in memory
2. **Bitmap buffer address** - Where bitmap data buffer is allocated

## Current Assets

✅ **Heap leak** - Can get heap addresses via type confusion
✅ **OOB read** - Can read from bitmap (though limited)
✅ **Use-after-free** - Can read variable table entries potentially

## Strategy 1: Calculation from Heap Leak (Simplest)

### Approach:
1. Leak string address (heap address)
2. Estimate variable entry is ~0x200-0x400 bytes before string
3. Estimate bitmap buffer is ~0x1000 bytes after string
4. Test and refine estimates

### Pros:
- Simple, no complex scanning
- Fast

### Cons:
- Estimates might be wrong
- Heap layout can vary

### Implementation:
```bitscript
int target = 0;
string target = "target";
int targetaddr = target;  // Leak heap address

// Estimate
entry_addr = targetaddr - 0x300;
value_ptr_addr = entry_addr + 0x28;
bitmap_data_ptr = targetaddr + 0x1000;
```

## Strategy 2: OOB Read to Scan Heap

### Approach:
1. Create bitmap with overflow
2. Use OOB read to scan heap backwards from known address
3. Look for variable entry patterns (name at offset 0x00, type at 0x20)
4. When found, that's the entry address

### Pros:
- More reliable
- Can find exact addresses

### Cons:
- Might cause segfaults
- Slow (need to scan systematically)

### Implementation:
```bitscript
bitmap b1 = create(9223372036854775807, 2);
// Scan backwards from targetaddr
// Look for "target" string at offset 0x00
// When found, that's entry_addr
```

## Strategy 3: Use-After-Free to Read Variable Table

### Approach:
1. Use self-assignment to create use-after-free
2. Allocate new objects that reuse freed memory
3. If we can control what gets allocated, we can read variable table entries

### Pros:
- Direct access to variable table
- Can read multiple entries

### Cons:
- Complex to control
- Might not work reliably

## Strategy 4: Heap Grooming + Calculation

### Approach:
1. Control allocation order
2. Use known offsets between allocations
3. Calculate addresses based on controlled layout

### Pros:
- Reliable if we control layout
- Can predict addresses

### Cons:
- Requires understanding heap allocator
- Might need many allocations

## Recommended Approach: Hybrid

**Start with Strategy 1 (Calculation), then refine:**

1. **Initial estimate:**
   ```bitscript
   entry_addr = targetaddr - 0x300;
   bitmap_data_ptr = targetaddr + 0x1000;
   ```

2. **Test estimate:**
   - Try to write test value to estimated address
   - If it works, addresses are correct
   - If not, adjust offset and retry

3. **Refine:**
   - Try different offsets: 0x200, 0x300, 0x400
   - Try different bitmap offsets: 0x800, 0x1000, 0x2000
   - Find what works

4. **Verify:**
   - Once write works, verify by reading back
   - Or verify by checking if variable behavior changes

## Implementation Plan

### Phase 1: Test Estimates
```bitscript
// Leak addresses
int target = 0;
string target = "target";
int targetaddr = target;

// Try different entry offsets
entry_addr_candidate1 = targetaddr - 0x200;
entry_addr_candidate2 = targetaddr - 0x300;
entry_addr_candidate3 = targetaddr - 0x400;

// Try to write test value to each
// See which one works
```

### Phase 2: Verify Address
```bitscript
// Once we think we found entry_addr:
// Write test value to value_ptr (entry_addr + 0x28)
// Then read: int test = target;
// If test == our test value, address is correct!
```

### Phase 3: Find Bitmap Buffer
```bitscript
// Create bitmap
bitmap b1 = create(9223372036854775807, 2);

// Try different offsets
bitmap_data_ptr_candidate1 = targetaddr + 0x800;
bitmap_data_ptr_candidate2 = targetaddr + 0x1000;
bitmap_data_ptr_candidate3 = targetaddr + 0x2000;

// Test by writing to known location and reading back
```

## Quick Test Script

Create a script that:
1. Leaks addresses
2. Tries multiple offset combinations
3. Tests each combination
4. Reports which one works

This is a brute-force approach, but it should work!

## Alternative: Use GDB

If you have access to GDB:
1. Set breakpoint after variable creation
2. Inspect heap
3. Find exact addresses
4. Use those in exploit

But for remote exploit, we need to find addresses programmatically.

## Next Action

**Create test script that tries multiple offset combinations!**

