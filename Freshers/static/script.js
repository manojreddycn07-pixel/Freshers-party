document.querySelectorAll('.button').forEach(button => {
  button.addEventListener('mousemove', event => {
    const box = button.getBoundingClientRect();
    button.style.transform = `translate(${(event.clientX - box.left - box.width / 2) * .06}px, ${(event.clientY - box.top - box.height / 2) * .06}px)`;
  });
  button.addEventListener('mouseleave', () => button.style.transform = '');
});
