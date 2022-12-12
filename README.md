# Protobuf Playground

[![Code Size](https://img.shields.io/github/languages/code-size/meysam81/protobuf-playground)](https://github.com/meysam81/protobuf-playground)
[![Repo Size](https://img.shields.io/github/repo-size/meysam81/protobuf-playground)](https://github.com/meysam81/protobuf-playground)
[![Language Count](https://img.shields.io/github/languages/count/meysam81/protobuf-playground)](https://github.com/meysam81/protobuf-playground)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=bugs)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=meysam81_protobuf-playground&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=meysam81_protobuf-playground)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Protobuf Playground](#protobuf-playground)
  - [Introduction](#introduction)
  - [Pre-requisites](#pre-requisites)
  - [Quick Start](#quick-start)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This repository serves as a playground & learning opportunity for me to
implement and wire different technologies together, resuling in both a learning
opportunity and a chance to get a feeling of what it's like to work with those
technologies.

I also tend to get benchmarking results for each implementation, so that I can
better understand the limitations and capabilities of each technology, better
helping me decide on my future projects when trying to pick the right tool for
the job.

The main focus of this repository will be to use **Protobuf** as the
serialization format. Everything else I'll add later on will be on top of that.
I tend to think that Protobuf is *the best* serialization format we have so far,
considering the performance efficiency and the human readability of the API.
It's also cross-platform, which makes it a great choice for distributed systems.

If you're interested in carrying along, or just want to add something to this
journey, feel free to open a PR or an issue.

If you're only interested in running the stack, you'll need to install the
required tools as described below.

## Pre-requisites

Sorted alphabetically:

- [alertmanager & amtool](https://prometheus.io/download/#alertmanager)
- [docker](https://docs.docker.com/install/)
- [etcd](https://github.com/etcd-io/etcd) [optional]
- [go](https://golang.org/dl/)
- [grpcurl](https://github.com/fullstorydev/grpcurl) [optional]
- [haproxy-exporter](https://prometheus.io/download/#haproxy_exporter)
- [haproxy](http://www.haproxy.org/)
- [jq](https://stedolan.github.io/jq/download/)
- [node-exporter](https://prometheus.io/download/#node_exporter)
- [prometheus & promtool](https://prometheus.io/download/#prometheus)
- [promlens](https://prometheus.io/download/#promlens)
- [protobuf](https://github.com/protocolbuffers/protobuf#protocol-compiler-installation)
- [python<=3.10](https://www.python.org/downloads/)
- [supervisord](http://supervisord.org/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) [optional]

## Quick Start

```bash
make install
make up
```
