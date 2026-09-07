export function validateRegistration({
  username,
  email,
  password,
  confirmPassword,
}) {
  const errors = {};
  if (!username.trim()) errors.username = "Введите логин.";
  else if (username.trim().length > 150)
    errors.username = "Логин должен быть не длиннее 150 символов.";
  if (!email.trim() || !/^\S+@\S+\.\S+$/.test(email.trim()))
    errors.email = "Введите корректный email.";
  if (password.length < 8)
    errors.password = "Пароль должен содержать минимум 8 символов.";
  if (password !== confirmPassword)
    errors.confirmPassword = "Пароли не совпадают.";
  return errors;
}
export function registrationErrors(error) {
  const data = error?.response?.data;
  const errors = {};
  if (data && typeof data === "object") {
    for (const key of ["username", "email", "password"]) {
      if (data[key])
        errors[key] = Array.isArray(data[key])
          ? data[key].join(" ")
          : String(data[key]);
    }
    const general = data.non_field_errors || data.detail;
    if (general)
      errors.form = Array.isArray(general)
        ? general.join(" ")
        : String(general);
  }
  if (!Object.keys(errors).length)
    errors.form = "Не удалось зарегистрироваться. Попробуйте ещё раз позже.";
  return errors;
}
