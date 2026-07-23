# Sherlock Storage

Sherlock provides several storage options for users:

## $HOME
- 15 GB quota, backed up nightly
- For scripts, source code, and small config files
- Not suitable for large datasets or job output

## $SCRATCH
- Large temporary storage, no quota, not backed up
- Files not accessed in 90 days are automatically deleted
- Use for job input/output and intermediate data

## $OAK
- Long-term research storage, quota varies by group
- Backed up, accessible from Sherlock and other clusters
- Best for data you need to keep between projects

## Checking your usage
```bash
df -h $HOME
lfs quota -u $USER /scratch
```
