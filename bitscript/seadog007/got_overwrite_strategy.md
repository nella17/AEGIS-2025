# GOT Overwrite Exploit Strategy

## Why This Will Work

✅ **Partial RELRO** - GOT is writable  
✅ **No PIE** - GOT address is fixed and known  
✅ **Heap Overflow** - We can write to heap, need to reach GOT  
✅ **Function Calls** - `print()` calls `printf()`, we can hijack it  

## Strategy

### Step 1: Find GOT Address

The GOT (Global Offset Table) stores addresses of imported functions.
- `printf@GOT` - Address where printf's address is stored
- When we overwrite this, `printf()` calls will go to our target

### Step 2: Find system@PLT

The PLT (Procedure Linkage Table) contains stubs that jump to functions.
- `system@PLT` - Address of system function
- We want to write this address to `printf@GOT`

### Step 3: Heap-to-GOT Write

**Challenge:** GOT is in `.got.plt` section, heap is separate.
**Solution:** 
- If heap and GOT are close, overflow might reach it
- Or use heap metadata corruption to get arbitrary write
- Or find a write primitive that uses corrupted heap pointer

### Step 4: Trigger Execution

After overwriting `printf@GOT` with `system@PLT`:
```bitscript
print("/bin/sh");
```
This will:
1. Call `printf("/bin/sh")` 
2. But GOT points to `system` instead
3. Executes `system("/bin/sh")` → **SHELL!**

## Alternative: Use Existing Function

If we can't reach GOT directly, we might:
1. Corrupt a function pointer in heap structure
2. Redirect to `system@PLT`
3. Trigger via corrupted structure access

## Next Steps

1. Run `./find_addresses.sh` to get GOT/PLT addresses
2. Check if heap overflow can reach GOT (unlikely, but check)
3. Look for write primitives using corrupted pointers
4. Craft payload to write `system@PLT` to `printf@GOT`
5. Call `print("/bin/sh")` to get shell

