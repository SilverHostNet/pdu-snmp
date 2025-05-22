import { createClient } from "../../supabase/server";

export const createServerClient = async () => {
  return await createClient();
};
