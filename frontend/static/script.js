(function () {
  'use strict';

  const card = document.getElementById('main-card');
  if (card) {
    requestAnimationFrame(() => {
      setTimeout(() => card.classList.add('is-visible'), 60);
    });
  }

  const recipientInput = document.getElementById('recipient');
  const avatar         = document.querySelector('.avatar');

  if (recipientInput && avatar) {
    recipientInput.addEventListener('focus', () => {
      avatar.style.background = 'rgba(76, 175, 120, 0.1)';
      avatar.style.borderColor = 'var(--color-accent)';
    });

    recipientInput.addEventListener('blur', () => {
      avatar.style.background  = '';
      avatar.style.borderColor = '';
    });
  }

  const bodyField = document.getElementById('body');

  if (bodyField) {
    bodyField.addEventListener('input', () => {
      bodyField.style.height = 'auto';
      bodyField.style.height = bodyField.scrollHeight + 'px';
    });
  }

  const form    = document.getElementById('email-form');
  const sendBtn = document.getElementById('send-btn');

  const shake = (el) => {
    if (!el) return;
    el.style.animation = 'none';
    void el.offsetWidth;
    el.style.animation = 'shake 350ms ease';
    el.addEventListener('animationend', () => {
      el.style.animation = '';
    }, { once: true });
  };

  const shakeStyle = document.createElement('style');
  shakeStyle.textContent = `
    @keyframes shake {
      0%   { transform: translate(3px, 3px); }
      20%  { transform: translate(-3px, 0); }
      40%  { transform: translate(3px, -2px); }
      60%  { transform: translate(-3px, 1px); }
      80%  { transform: translate(2px, -1px); }
      100% { transform: translate(0, 0); }
    }
  `;
  document.head.appendChild(shakeStyle);

  if (form) {
    form.addEventListener('submit', (e) => {
      if (!form.checkValidity()) {
        e.preventDefault();
        shake(sendBtn);

        form.querySelectorAll('[required]').forEach((field) => {
          if (!field.value.trim()) {
            field.style.borderColor = '#e05252';
            field.style.boxShadow   = '0 0 0 3px rgba(224,82,82,0.15)';

            field.addEventListener('input', () => {
              field.style.borderColor = '';
              field.style.boxShadow   = '';
            }, { once: true });
          }
        });
      }
    });
  }

  const feedback = document.getElementById('feedback');

  document.body.addEventListener('htmx:beforeRequest', () => {
    if (sendBtn) sendBtn.disabled = true;
    if (feedback) {
      feedback.textContent = '';
      feedback.className   = 'feedback';
    }
  });

  document.body.addEventListener('htmx:afterRequest', (e) => {
    if (sendBtn) sendBtn.disabled = false;

    if (!feedback) return;

    const ok = e.detail.xhr.status >= 200 && e.detail.xhr.status < 300;
    if (ok) {
      feedback.textContent = '✓ Email enviado com sucesso!';
      feedback.classList.remove('is-error');

      if (form) {
        setTimeout(() => {
          form.reset();
          if (bodyField) bodyField.style.height = '';
        }, 800);
      }
    } else {
      feedback.textContent = '✗ Falha ao enviar. Tente novamente.';
      feedback.classList.add('is-error');
      shake(sendBtn);
    }
  });

  document.body.addEventListener('htmx:sendError', () => {
    if (sendBtn) sendBtn.disabled = false;
    if (feedback) {
      feedback.textContent = '✗ Sem conexão com o servidor.';
      feedback.classList.add('is-error');
    }
  });

})();
