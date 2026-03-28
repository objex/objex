class Objex < Formula
  include Language::Python::Virtualenv

  desc "CLI for registering with Objex and scanning codebases into OpenAPI specs"
  homepage "https://github.com/objex/objex"
  head "https://github.com/objex/objex.git", branch: "main"
  license "Apache-2.0"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Objex CLI service", shell_output("#{bin}/objex --help")
  end
end
