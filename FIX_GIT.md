# Fix: Remove Large CSV from Git History

Your CSV file (1.26 GB) is stuck in Git history. Here's how to fix it:

## Quick Fix: Reset and Recommit

1. **Cancel the current push** (if still running)

2. **Reset to before CSV was added**:
   ```bash
   git reset --soft 0a47519
   ```

3. **Unstage the CSV** (if any):
   ```bash
   git reset HEAD backend/crashes_cleaned.csv
   ```

4. **Commit only code changes**:
   ```bash
   git commit -m "Update app to download CSV from URL, fix Python version"
   ```

5. **Force push** (since we rewrote history):
   ```bash
   git push origin main --force
   ```

## Alternative: Use Git Filter to Remove File from History

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/crashes_cleaned.csv" \
  --prune-empty --tag-name-filter cat -- --all
```

Then force push:
```bash
git push origin main --force
```

## Simplest Solution: Start Fresh Branch

1. Create new branch without CSV:
   ```bash
   git checkout -b main-clean 0a47519
   ```

2. Cherry-pick good commits (without CSV):
   ```bash
   git cherry-pick 8775966  # Update app to download CSV
   git cherry-pick 413051a  # Remove CSV from gitignore
   ```

3. Push new branch:
   ```bash
   git push origin main-clean:main --force
   ```

---

**RECOMMENDATION**: Use the reset method (Quick Fix) - it's fastest!

