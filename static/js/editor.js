(function () {
    var shell = document.querySelector(".editor-shell");
    if (!shell) {
        return;
    }

    var problemSlug = shell.dataset.problemSlug;
    var languageSelect = document.getElementById("languageSelect");
    var runBtn = document.getElementById("runBtn");
    var submitBtn = document.getElementById("submitBtn");
    var stdinInput = document.getElementById("stdinInput");
    var statusNode = document.getElementById("judgeStatus");
    var outputConsole = document.getElementById("outputConsole");
    var fallbackEditor = document.getElementById("fallbackEditor");
    var monacoBox = document.getElementById("monacoEditor");
    var starterCode = JSON.parse(document.getElementById("starter-code-data").textContent);
    var monacoEditor = null;
    var languageMap = {
        python: "python",
        c: "c",
        cpp: "cpp",
        java: "java"
    };

    function setConsoleTab(name) {
        document.querySelectorAll("[data-console-tab]").forEach(function (button) {
            button.classList.toggle("active", button.dataset.consoleTab === name);
        });
        document.getElementById("inputPanel").classList.toggle("active", name === "input");
        document.getElementById("outputPanel").classList.toggle("active", name === "output");
    }

    function setStatus(text, tone) {
        statusNode.textContent = text;
        statusNode.style.color = tone || "";
    }

    function setLoading(isLoading) {
        runBtn.disabled = isLoading;
        submitBtn.disabled = isLoading;
        runBtn.innerHTML = isLoading ? '<span class="spinner-border spinner-border-sm me-1"></span>Running' : '<i class="bi bi-play-fill me-1"></i>Run';
        submitBtn.innerHTML = isLoading ? '<span class="spinner-border spinner-border-sm me-1"></span>Submitting' : '<i class="bi bi-send-fill me-1"></i>Submit';
    }

    function getCode() {
        if (monacoEditor) {
            return monacoEditor.getValue();
        }
        return fallbackEditor.value;
    }

    function setCodeForLanguage(language) {
        var code = starterCode[language] || "";
        if (monacoEditor) {
            monacoEditor.setValue(code);
            monaco.editor.setModelLanguage(monacoEditor.getModel(), languageMap[language] || "plaintext");
        }
        fallbackEditor.value = code;
    }

    function showOutput(title, body, isSuccess) {
        setConsoleTab("output");
        setStatus(title, isSuccess ? "#57f29a" : "#ff667a");
        outputConsole.textContent = body || "No output.";
    }

    function sendJudgeRequest(url) {
        setLoading(true);
        setConsoleTab("output");
        setStatus("Executing...", "#38e8ff");
        outputConsole.textContent = "Judge is compiling/running your solution.";

        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.getCookie("csrftoken")
            },
            body: JSON.stringify({
                problem_slug: problemSlug,
                language: languageSelect.value,
                code: getCode(),
                stdin: stdinInput.value
            })
        }).then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        }).catch(function (error) {
            return {
                ok: false,
                data: {
                    verdict: "Runtime Error",
                    stderr: "Request failed: " + error.message
                }
            };
        }).finally(function () {
            setLoading(false);
        });
    }

    document.querySelectorAll("[data-console-tab]").forEach(function (button) {
        button.addEventListener("click", function () {
            setConsoleTab(button.dataset.consoleTab);
        });
    });

    languageSelect.addEventListener("change", function () {
        setCodeForLanguage(languageSelect.value);
    });

    runBtn.addEventListener("click", function () {
        sendJudgeRequest("/submissions/run/").then(function (response) {
            var data = response.data;
            var output = [
                "Verdict: " + (data.verdict || "OK"),
                "Time: " + (data.execution_time || 0) + "s",
                "",
                "STDOUT:",
                data.stdout || "",
                "",
                "STDERR:",
                data.stderr || data.message || ""
            ].join("\n");
            showOutput(data.verdict || "Run Complete", output, response.ok);
        });
    });

    submitBtn.addEventListener("click", function () {
        sendJudgeRequest("/submissions/submit/").then(function (response) {
            var data = response.data;
            var output = [
                "Verdict: " + data.verdict,
                "Time: " + (data.execution_time || 0) + "s",
                "Failed Test: " + (data.failed_test_number || "-"),
                "",
                data.output || "",
                data.error_message || ""
            ].join("\n");
            showOutput(data.verdict || "Submission Complete", output, data.verdict === "Accepted");
        });
    });

    function initFallback() {
        monacoBox.style.display = "none";
        fallbackEditor.style.display = "block";
        setCodeForLanguage(languageSelect.value);
    }

    if (window.require) {
        window.require.config({ paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs" } });
        window.require(["vs/editor/editor.main"], function () {
            monacoEditor = monaco.editor.create(monacoBox, {
                value: starterCode[languageSelect.value] || "",
                language: languageMap[languageSelect.value],
                theme: "vs-dark",
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 15,
                lineNumbersMinChars: 3,
                scrollBeyondLastLine: false,
                padding: { top: 16, bottom: 16 }
            });
            fallbackEditor.value = monacoEditor.getValue();
        }, initFallback);
    } else {
        initFallback();
    }
})();
