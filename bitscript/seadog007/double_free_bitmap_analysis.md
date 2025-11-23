# Double Free in Bitmap Assignment

## Location
`eval_statement` function, ASSIGNMENT case (case 4), lines 71-76

## The Vulnerability

**Code Flow for `b2 = b1;`:**

```c
case 4:  // ASSIGNMENT
  v9 = get_variable("b2");  // Get target variable (b2)
  v8 = v9;
  eval_expression(v3, b1_ast);  // Evaluate source (b1)
  // v5 = pointer to b1's bitmap struct
  
  if ( *(_DWORD *)(v8 + 32) == 2 && *(_QWORD *)(v8 + 40) ) {  // If bitmap and has old value
    free(*(void **)(*(_QWORD *)(v8 + 40) + 16LL));  // Free old bitmap data
    free(*(void **)(v8 + 40));  // Free old bitmap struct
  }
  *(_QWORD *)(v8 + 40) = v5;  // Set b2.value_ptr = b1.value_ptr
```

## The Problem

**After `b2 = b1;`:**

1. **b2's old bitmap is freed** (the 20x20 bitmap)
2. **b2.value_ptr is set to b1.value_ptr** (pointer copy, NOT deep copy!)
3. **Both variables now point to the SAME bitmap struct!**

**Memory State:**
```
b1.value_ptr → [Bitmap struct: 10x10]
b2.value_ptr → [Same bitmap struct] ← SHARED!
```

## Double Free Scenarios

### Scenario 1: Delete Both Variables

```bitscript
bitmap b1 = create(10, 10);
bitmap b2 = create(20, 20);
b2 = b1;  // Both point to same struct
delete(b2);    // Frees the shared bitmap struct
delete(b1);    // Tries to free the SAME struct → DOUBLE FREE!
```

### Scenario 2: Reassign Both Variables

```bitscript
bitmap b1 = create(10, 10);
bitmap b2 = create(20, 20);
b2 = b1;  // Both point to same struct
b2 = create(30, 30);  // Frees the shared struct
b1 = create(40, 40);   // Tries to free the SAME struct → DOUBLE FREE!
```

### Scenario 3: Cleanup Phase

```bitscript
bitmap b1 = create(10, 10);
bitmap b2 = create(20, 20);
b2 = b1;  // Both point to same struct
// Script completes
// Cleanup tries to free both → DOUBLE FREE!
```

## Root Cause

**Same as string assignment:** Bitmap assignment does a **shallow copy** (pointer copy) instead of a **deep copy**.

**What should happen:**
```c
// Should create a copy:
new_bitmap_struct = malloc(0x18);
new_bitmap_data = malloc(width * height / 8);
memcpy(new_bitmap_data, old_bitmap_data, size);
new_bitmap_struct->width = old_bitmap_struct->width;
new_bitmap_struct->height = old_bitmap_struct->height;
new_bitmap_struct->data = new_bitmap_data;
b2.value_ptr = new_bitmap_struct;  // New copy!
```

**What actually happens:**
```c
b2.value_ptr = b1.value_ptr;  // Just copies pointer!
```

## Exploitation Potential

**Same as string double free:**
- Heap corruption
- Fastbin/tcache attack
- Arbitrary write
- RCE

## Proof of Concept

See `poc_double_free_bitmap.bs`

