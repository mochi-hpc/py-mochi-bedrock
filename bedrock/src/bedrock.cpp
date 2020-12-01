/*
 * (C) 2018 The University of Chicago
 *
 * See COPYRIGHT in top-level directory.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <bedrock/Client.hpp>
#include <bedrock/ServiceHandle.hpp>
#include <bedrock/Exception.hpp>

namespace py11 = pybind11;
using namespace pybind11::literals;
using namespace bedrock;

struct margo_instance;
typedef struct margo_instance* margo_instance_id;
typedef py11::capsule pymargo_instance_id;

#define MID2CAPSULE(__mid)   py11::capsule((void*)(__mid), "margo_instance_id", nullptr)
#define CAPSULE2MID(__caps)  (margo_instance_id)(__caps)

PYBIND11_MODULE(_pybedrock, m) {
    m.doc() = "Bedrock client C++ extension";
    py11::register_exception<Exception>(m, "Exception", PyExc_RuntimeError);
    py11::class_<Client>(m, "Client")
        .def(py11::init<pymargo_instance_id>())
        .def("create_service_handle",
             &Client::makeServiceHandle,
             "Create a ServiceHandle instance",
             "address"_a,
             "provider_id"_a=0);
    py11::class_<ServiceHandle>(m, "ServiceHandle")
        .def("get_config",
             [](const ServiceHandle& sh) {
                std::string config;
                sh.getConfig(&config);
                return std::move(config);
             })
    ;
}
