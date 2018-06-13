var spawn = require('child_process').spawn;
var app   = spawn('python3.6', ['purinAI.py']); //言語名とファイル名を記述する
app.stdout.on('data', function(data) {{
  console.log('stdout: ' + data);
}});

app.stderr.on('data', function(data) {{
  console.log('stderr: ' + data);
}});

app.on('exit', function(code) {{
  console.log('exit code: ' + code);
}});