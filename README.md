# 🔐 HashHunter

A lightweight, colorful, CLI-based **Hash Identifier & Wordlist Cracker** built for ethical hackers and CTF players on **Kali Linux**.

---

## 🚀 Features

- ✅ Auto hash type identification
- ✅ Single hash cracking
- ✅ Batch cracking (file of hashes)
- ✅ Hash generation for testing
- ✅ Progress display with words/sec rate
- ✅ Save results to output file
- ✅ Colored terminal output

---

## 🔑 Supported Hash Types

| Type   | Length |
|--------|--------|
| MD5    | 32     |
| SHA1   | 40     |
| SHA224 | 56     |
| SHA256 | 64     |
| SHA384 | 96     |
| SHA512 | 128    |

---

## 📦 Installation

```bash
git clone https://github.com/yourhandle/hashhunter
cd hashhunter
python3 hashhunter.py --help
```

> No external dependencies. Uses Python standard library only.

---

## 🛠️ Usage

### Crack a single hash
```bash
python3 hashhunter.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w /usr/share/wordlists/rockyou.txt
```

### Force hash type manually
```bash
python3 hashhunter.py -H <hash> -w rockyou.txt -t SHA256
```

### Crack multiple hashes from a file
```bash
python3 hashhunter.py -f hashes.txt -w rockyou.txt -o results.txt
```

### Identify hash type only (no cracking)
```bash
python3 hashhunter.py --identify 5f4dcc3b5aa765d61d8327deb882cf99
```

### Generate a hash for testing
```bash
python3 hashhunter.py --generate "password123" --type MD5
```

### Verbose mode (show progress)
```bash
python3 hashhunter.py -H <hash> -w rockyou.txt -v
```

---

## 📁 Hash File Format (for batch mode)

One hash per line:
```
5f4dcc3b5aa765d61d8327deb882cf99
e10adc3949ba59abbe56e057f20f883e
```

---

## 📋 Output File Format

```
<hash>:<type>:<plaintext>
5f4dcc3b5aa765d61d8327deb882cf99:MD5:"password"
```

---

## ⚠️ Disclaimer

This tool is intended for **educational purposes**, **CTF challenges**, and **authorized penetration testing only**.  
Unauthorized use against systems you do not own is **illegal**.  
The author is not responsible for any misuse.

---

## 📜 License

MIT License
