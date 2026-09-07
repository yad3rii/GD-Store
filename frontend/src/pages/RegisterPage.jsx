import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { register } from "../api/auth";
import {
  validateRegistration,
  registrationErrors,
} from "../utils/registration";
export default function RegisterPage() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [pending, setPending] = useState(false);
  const [success, setSuccess] = useState(false);
  const sending = useRef(false);
  const submit = async (event) => {
    event.preventDefault();
    if (sending.current) return;
    const validation = validateRegistration(form);
    setErrors(validation);
    if (Object.keys(validation).length) return;
    sending.current = true;
    setPending(true);
    try {
      await register({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
      });
      setForm({ username: "", email: "", password: "", confirmPassword: "" });
      setSuccess(true);
    } catch (error) {
      setErrors(registrationErrors(error));
    } finally {
      sending.current = false;
      setPending(false);
    }
  };
  if (success)
    return (
      <section className="auth-panel" role="status">
        <p className="eyebrow">Добро пожаловать</p>
        <h1>Аккаунт создан</h1>
        <p>Теперь вы можете войти и начать собирать свою коллекцию.</p>
        <Link className="button primary" to="/login">
          Войти в аккаунт
        </Link>
      </section>
    );
  return (
    <form
      className="auth-panel"
      onSubmit={submit}
      aria-busy={pending}
      noValidate
    >
      <p className="eyebrow">Ваша история начинается здесь</p>
      <h1>Создать аккаунт</h1>
      <p>Сохраняйте игры и собирайте свою коллекцию.</p>
      {[
        ["username", "Логин", "text", "username"],
        ["email", "Email", "email", "email"],
        ["password", "Пароль", "password", "new-password"],
        ["confirmPassword", "Повторите пароль", "password", "new-password"],
      ].map(([name, label, type, autoComplete]) => (
        <label key={name} htmlFor={`register-${name}`}>
          {label}
          <input
            id={`register-${name}`}
            name={name}
            type={type}
            autoComplete={autoComplete}
            required
            disabled={pending}
            maxLength={name === "username" ? 150 : undefined}
            value={form[name]}
            onChange={(event) => {
              setForm({ ...form, [name]: event.target.value });
              setErrors((current) => ({
                ...current,
                [name]: undefined,
                form: undefined,
              }));
            }}
            aria-invalid={!!errors[name]}
            aria-describedby={
              errors[name]
                ? `${name}-error`
                : name === "password"
                  ? "password-hint"
                  : undefined
            }
          />
          {name === "password" && !errors.password && (
            <span id="password-hint" className="field-hint">
              Не менее 8 символов
            </span>
          )}
          {errors[name] && (
            <span id={`${name}-error`} className="field-error" role="alert">
              {errors[name]}
            </span>
          )}
        </label>
      ))}
      {errors.form && (
        <p className="error-message" role="alert">
          {errors.form}
        </p>
      )}
      <button className="button primary" disabled={pending}>
        {pending ? "Создаём аккаунт…" : "Зарегистрироваться"}
      </button>
      <p>
        Уже есть аккаунт?{" "}
        <Link className="text-link" to="/login">
          Войти
        </Link>
      </p>
      <Link className="text-link" to="/">
        ← Вернуться в магазин
      </Link>
    </form>
  );
}
