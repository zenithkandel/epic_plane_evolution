# Epic Plane Evolution: Complete Cheat Engine Memory Reverse Engineering & Currency Manipulation Guide

---

## 1. Executive Summary & Architecture

"Epic Plane Evolution" is a Unity WebGL game compiled with **IL2CPP** running inside a Chromium-based browser (Brave / Chrome) over WebAssembly (WASM).

### The Technical Challenge
Traditional memory hacking in browser games fails in this game once currency exceeds **2.14 Billion** ($2^{31} - 1$). At that threshold:
1. Normal 4-byte scans for the displayed coin count return 0 results.
2. The memory address that previously held coins suddenly drops to `1`.
3. Writing numbers directly to the old address no longer changes in-game money.

This occurs because the game utilizes .NET's **`System.Numerics.BigInteger`** to handle arbitrary-precision currency, combined with the **32-bit WASM Linear Memory Sandbox** inside a 64-bit browser process.

---

## 2. Core Concepts: How BigInteger Works in Memory

In Unity IL2CPP (32-bit WASM runtime), `System.Numerics.BigInteger` is an immutable 8-byte structure:

```cpp
struct BigInteger {
    int32_t  _sign;   // Offset +0x00 (4 bytes)
    uint32_t _bits;   // Offset +0x04 (4-byte pointer to uint32_t[] array)
};
```

### State A: Small Currency ($\le 2,147,483,647$)
* `_bits` is **`NULL` (`0x00000000`)**.
* `_sign` holds the **exact raw coin count** as a signed 32-bit integer.
* *Behavior:* A standard Cheat Engine 4-byte scan directly finds `_sign`.

### State B: Large Currency ($> 2,147,483,647$)
* Once coins cross $2^{31} - 1$, a 32-bit signed integer would overflow.
* The engine switches representation:
  * `_sign` is set to **`1`** (a flag signifying positive value).
  * `_bits` is assigned a **32-bit heap pointer** pointing to a dynamically allocated `uint32[]` array in WASM memory.
* *Behavior:* This is why Cheat Engine showed the value as `1`. The actual money was moved into the array referenced by `_bits`.

```
Permanent Object (coinsAmount):
[ Address: 28501CC2B0C ]
+-------------------+-------------------+
|  _sign (4 bytes)  |  _bits (4 bytes)  |
|    01 00 00 00    |    00 0F 27 0E    |
+-------------------+-------------------+
          |                   |
      Sign = +1         Pointer = 0x0E270F00 (WASM offset)
                              |
                              v
                  [ Base: 0x28500000000 + 0x0E270F00 ]
                  Array Object in Heap:
                  +0x00: IL2CPP Klass Pointer
                  +0x04: Monitor / SyncBlock
                  +0x08: Bounds
                  +0x0C: Array Length (uint32)
                  +0x10: Chunk 1 (_bits[0] - Lower 32 bits)
                  +0x14: Chunk 2 (_bits[1] - Upper 32 bits / Multiplier)
```

---

## 3. The IL2CPP Array Memory Layout (WASM 32-bit)

When `_bits` points to an array, the target memory follows standard IL2CPP array formatting:

| Offset from Array Base | Field | Type | Description |
| :--- | :--- | :--- | :--- |
| **`+ 0x00`** | Klass Pointer | 4 Bytes | Pointer to `System.UInt32[]` class descriptor |
| **`+ 0x04`** | Monitor | 4 Bytes | Synchronization block header |
| **`+ 0x08`** | Bounds Pointer | 4 Bytes | Array bounds descriptor |
| **`+ 0x0C`** | **Array Length** | 4 Bytes | Number of elements in the array |
| **`+ 0x10`** | **Chunk 1 (`_bits[0]`)**| 4 Bytes | Lower 32 bits (holds values from $0$ to $4,294,967,295$) |
| **`+ 0x14`** | **Chunk 2 (`_bits[1]`)**| 4 Bytes | Multiplier for $2^{32}$ ($\approx 4.294967\text{B}$) |
| **`+ 0x18`** | Chunk 3 (`_bits[2]`)| 4 Bytes | Multiplier for $2^{64}$ (only needed for Quintillions+) |

---

## 4. The Currency Formula & Calculations

The value of the currency is computed as:
$$\text{Total Coins} = \text{Chunk 1} + (\text{Chunk 2} \times 2^{32})$$
$$\text{where } 2^{32} = 4,294,967,296$$

### How to Calculate Chunks for Any Target Amount
To generate any desired coin amount:
1. **$\text{Chunk 2} = \lfloor \text{Target} / 4,294,967,296 \rfloor$** (Integer division)
2. **$\text{Chunk 1} = \text{Target} \pmod{4,294,967,296}$** (Remainder)
3. **$\text{Array Length} = 2$** (Must be at least 2 so the game reads both chunks)

### Quick Reference Table
| Target Money | Chunk 1 (`_bits[0]`) | Chunk 2 (`_bits[1]`) | Array Length |
| :--- | :--- | :--- | :--- |
| **10 Billion (10B)** | `1410065408` | `2` | `2` |
| **100 Billion (100B)** | `1215752192` | `23` | `2` |
| **1 Trillion (1T)** | `3567587328` | `232` | `2` |
| **20 Trillion (20T)** | `2632269824` | `4656` | `2` |
| **500 Trillion (500T)** | **`1382236160`** | **`116415`** | `2` |
| **1 Quadrillion (1Q)** | `2764472320` | `232830` | `2` |

---

## 5. Why Edits Stop Working: The Immutability Reallocation Issue

If you modify Chunk 1 and Chunk 2 and see no effect, or the values suddenly reset, this is due to **C# Immutability**:

1. In .NET, `System.Numerics.BigInteger` is an **immutable struct**. 
2. Whenever any arithmetic happens (earning offline income, collecting flight rewards, or purchasing an upgrade):
   $$\text{coinsAmount}_{\text{new}} = \text{coinsAmount}_{\text{old}} \pm \Delta$$
3. Because it is immutable, the game **never overwrites the existing array in place**. Instead, it:
   - Allocates a **new `uint[]` array** at a different memory address on the garbage-collected heap.
   - Calculates the new value and writes it into this new array.
   - Updates the pointer at `_bits` (`coinsAmount + 0x4`) to point to the new array.
   - Abandons the old array for the garbage collector.
4. **The Consequence:** If the game ticks passive income before you make your move, the address you were editing is already orphaned.

---

## 6. Complete Operator Guide (Step-by-Step)

Follow this exact procedure to locate, calculate, and modify money reliably:

### Step 1: Attach Cheat Engine to the Browser
1. In Brave/Chrome, press `Shift + Esc` to view Chrome's internal Task Manager.
2. Find the tab named **"YT Game Wrapper WebGL"** (or the game frame) and note its **Process ID (PID)**.
3. In Cheat Engine, click the **Process List** button $\rightarrow$ switch to the **Processes** tab $\rightarrow$ select the matching hex PID (e.g. `000066D0-brave.exe`).

### Step 2: Locate the `coinsAmount` Object Address
1. Start with your coins below 2 Billion (spend or restart if necessary).
2. Scan for your current coin count (`4 Bytes`).
3. Fly or upgrade once to change coins, then scan for `Increased value` or the exact new number.
4. When you isolate the address, you have found `_sign`.
   *(In your session, this was at `...1CC2B0C`).*

### Step 3: Find the Dynamic Array Address
1. Right-click the found address $\rightarrow$ select **Browse this memory region** (Memory Viewer).
2. Look at the 8 bytes starting at your address:
   - First 4 bytes (`+0x00`): `_sign` (shows `01 00 00 00` when $> 2.14\text{B}$).
   - Next 4 bytes (`+0x04`): `_bits` pointer (e.g., `00 0F 27 0E`).
3. Reverse the 4 bytes from Little-Endian to Hex:
   - `00 0F 27 0E` $\rightarrow$ `0x0E270F00`.
4. Look at the title/header of the Memory Viewer for `AllocationBase` (e.g., `AllocationBase=28500000000`).
5. Add the base and offset:
   $$\text{Array Base} = \text{AllocationBase} + \text{Pointer} = \text{0x28500000000} + \text{0x0E270F00} = \mathbf{\text{0x2850E270F00}}$$

### Step 4: The Dynamic Pointer Method (The "Never-Lose-Address" Setup)
Instead of manually recalculating addresses every time the game moves the array, you can set up Cheat Engine to **automatically follow the pointer**:

1. In Cheat Engine, click **Add Address Manually**.
2. Check the **[X] Pointer** box.
3. In the base address field at the bottom, enter the `_bits` address (e.g. `28501CC2B10`).
4. Set the offset:
   - For **Array Length**: Offset = `C`
   - For **Chunk 1 (Real Money)**: Offset = `10`
   - For **Chunk 2 (Multiplier)**: Offset = `14`
5. Cheat Engine will now automatically resolve and update the memory location whenever the game reallocates the array!

### Step 5: Applying the Values Without Crashing
1. **Pause Game Execution:** Click **Settings** in CE or use hotkeys (or simply pause before an income tick).
2. Ensure **Array Length** is set to `2`.
3. Set **Chunk 1** to `1382236160` (for 500T).
4. Set **Chunk 2** to `116415` (for 500T).
5. Unpause the game and click any upgrade button or fly once.
6. The UI immediately reads the two chunks and displays **`500T`**.

---

## 7. Troubleshooting & Recovery Checklist

* **Q: I modified Chunk 1 and Chunk 2, but the game still displays the old value.**
  * *Reason:* An income tick triggered and generated a new array pointer right before your edit.
  * *Fix:* Check `_bits` in Memory Viewer. If the 4 bytes changed, recalculate the array address or use the **Pointer Method** from Step 4.

* **Q: The game crashed after editing.**
  * *Reason:* You modified an upgrade level index (e.g., `incomeLevel`) beyond its array bounds, or set `Array Length` to a number smaller than the chunks being read.
  * *Fix:* Always keep `Array Length` set to `2` or higher when editing Chunk 2. Never edit game level indexes beyond known limits.

* **Q: Cheat Engine cannot find the value when scanning.**
  * *Reason:* You attached to the Chrome/Brave GPU or Broker process instead of the dedicated Renderer tab process.
  * *Fix:* Use Chrome Task Manager (`Shift + Esc`) to find the exact tab PID.

