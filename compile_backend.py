import py_compile, glob, sys
files = glob.glob('Backend/*.py')
errs = False
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print('OK:', f)
    except Exception as e:
        print('ERR:', f, e)
        errs = True
if errs:
    sys.exit(1)
else:
    print('All compiled successfully')
