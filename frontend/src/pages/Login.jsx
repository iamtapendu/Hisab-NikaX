import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema } from "../modules/auth/schema";
import { loginUser } from "../modules/auth/service";
import InputWithPopup from '../components/InputWithPopup'
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/app/providers/auth-context";
import { useState } from "react";
import Modal from "@/components/Modal";
import Spinner from "@/components/Spinner";


export default function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const navigate = useNavigate();
  const { login } = useAuth();

  const [modalMsg, setModalMsg] = useState("");
  const [modalOpen, setModalOpen] = useState(false);


  const onSubmit = async (values) => {
    try {
      const tokens = await loginUser(values);

      login(tokens);
      navigate("/home", { replace: true })

      console.log("[login Success]")
    } catch (error) {
      setModalMsg(error.msg || "Login failed");
      setModalOpen(true);
      console.log("[Login Failed]", error.msg, error.errors)
    }
  };

  return (
    <div className="p-10 rounded-md shadow-lg shadow-primary">
      <h1 className="text-2xl font-bold m-2">Login</h1>
      <form className="grid grid-cols-1 md:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <InputWithPopup name="username" placeholder="Username" register={register} error={errors.username} />
        <InputWithPopup name="password" type="password" placeholder="Password" register={register} error={errors.password} />
        <button type="submit" className="btn btn-primary md:col-span-2 m-1" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
          {isSubmitting && <Spinner/>}
        </button>
      </form>
      <Modal
        open={modalOpen}
        message={modalMsg}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}

