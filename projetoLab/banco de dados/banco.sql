create database project_equilibrio;
use project_equilibrio;

CREATE TABLE diagnosticos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    genero ENUM('Masculino', 'Feminino', 'Não-binário', 'Prefiro não informar') DEFAULT NULL,
    idade INT DEFAULT NULL CHECK (idade >= 16 AND idade <= 100),
    pressao_academica INT DEFAULT NULL CHECK (pressao_academica >= 0 AND pressao_academica <= 5),
    rendimento_academico INT DEFAULT NULL CHECK (rendimento_academico >= 0 AND rendimento_academico <= 10),
    satisfacao_estudo INT DEFAULT NULL CHECK (satisfacao_estudo >= 0 AND satisfacao_estudo <= 5),
    duracao_sono INT DEFAULT NULL CHECK (duracao_sono >= 1 AND duracao_sono <= 24),
    habitos_alimentares ENUM('Pouco', 'Moderado', 'Muito') DEFAULT NULL,
    grau_academico ENUM('Ensino Médio', 'Graduação', 'Pós-graduação', 'Mestrado', 'Doutorado') DEFAULT NULL,
    pensamento_suicida ENUM('Não', 'Sim') DEFAULT NULL,
    horas_estudando INT DEFAULT NULL CHECK (horas_estudando >= 0 AND horas_estudando <= 24),
    pressao_financeira INT DEFAULT NULL CHECK (pressao_financeira >= 0 AND pressao_financeira <= 10),
    historico_familiar ENUM('Não', 'Sim') DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
