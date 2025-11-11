
function togglePassword(fieldId, iconElement) {
  const input = document.getElementById(fieldId);
  if (input.type === "password") {
    input.type = "text";
    iconElement.innerHTML = '<i class="fa fa-eye-slash"></i>';
  } else {
    input.type = "password";
    iconElement.innerHTML = '<i class="fa fa-eye"></i>';
  }
}

