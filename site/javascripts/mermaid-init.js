function initializeMermaid() {
  if (!window.mermaid) {
    return;
  }

  window.mermaid.initialize({
    startOnLoad: false,
    theme: "neutral",
    securityLevel: "loose",
  });

  window.mermaid.run({
    querySelector: ".mermaid",
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(function () {
    initializeMermaid();
  });
} else {
  window.addEventListener("load", function () {
    initializeMermaid();
  });
}
